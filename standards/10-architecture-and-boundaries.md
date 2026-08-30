# 10. Architecture & Module Boundaries

Sections 3 through 6 govern what a single file looks like. This section governs what the files are allowed to know about each other — which is the thing that actually determines whether a codebase stays workable at year three, and the thing a style guide most often leaves unsaid.

There is one architectural constraint this project has already committed to, and everything else here follows from it: **`core` contains no Qt.**

## 10.1 The core/GUI boundary

#### 10.1.1 core is Qt-free, with no exceptions

**RULE**  No file under `core/` includes any Qt header, names any Qt type, links any Qt module, or uses any Qt macro (`Q_OBJECT`, `Q_PROPERTY`, `signals`, `slots`, `emit`). This includes the ostensibly non-GUI parts of Qt: `QString`, `QVector`, `QFile`, `QObject`, and `QDebug` are as prohibited in `core` as `QWidget` is. Domain types in `core` use standard-library equivalents — `std::string`, `std::vector`, `std::filesystem::path`. Conversion between standard types and Qt types happens in `gui/`, at the boundary, and nowhere else.

**RATIONALE**  Three things follow from this and would be lost without it. First, `core` is testable without a Qt runtime — no `QApplication`, no event loop, no GUI thread — which is what makes the GoogleTest half of Section 12 possible and fast. Second, `core` is buildable and portable independently of Qt's own platform support, so a future headless tool, a command-line batch mode, or a Linux port (Section 9) is a linking exercise rather than a rewrite. Third, and most importantly in practice, the rule is *mechanically checkable* in a way "keep the GUI separate from the logic" is not: a `#include <QString>` under `core/` is a fact a grep can find, whereas "is this business logic" is an argument nobody wins in review. A boundary that can be checked is a boundary that survives.

Allowing `QString` "just for convenience" is the specific way this rule dies, which is why it is named explicitly — the moment one non-GUI Qt type is permitted, the line moves from "no Qt" to "which Qt," and the second question has no stable answer.

**GOOD**

```cpp
// core/io/hdf5reader.h -- standard types only
class Hdf5Reader
{
public:
    explicit Hdf5Reader(std::filesystem::path path);
    [[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(std::string_view datasetName);
};
```

```cpp
// gui/models/record_table_model.cpp -- conversion happens here, at the boundary
QVariant RecordTableModel::data(const QModelIndex& index, int role) const
{
    const core::Record& record = batch.records[static_cast<size_t>(index.row())];
    return QString::fromStdString(record.name());   // std::string -> QString, in gui/
}
```

**BAD**

```cpp
// core/io/hdf5reader.h
#include <QString>                                  // BAD -- Qt header under core/

class Hdf5Reader
{
public:
    QString datasetName() const;                    // BAD -- Qt type in a core interface
};
```

```cpp
// core/io/hdf5reader.cpp
qDebug() << "opened" << path;   // BAD -- Qt logging in core; see Section 13
```

**ENFORCEMENT**  Build failure is the real gate for anything requiring a Qt module to link, since `core` never links one (8.1.2). Header-only usage would still compile if a Qt include path leaked in, so this is backed by a grep for `#include <Q` and `#include <Qt` under `core/`, listed in Section 7 as a CI candidate and performed by the reviewer during the manual review (1.8) until then.

#### 10.1.2 Dependencies flow one way: app depends on gui depends on core

**RULE**  `core` knows nothing about `gui` or `app`. `gui` may use `core`. `app` may use both. A lower layer never calls up into a higher one — not by include, not by function call, not by a callback the lower layer defines and the upper layer sets, if that callback exists to let `core` drive the GUI. Where `core` genuinely needs to report progress or state upward, it does so through an interface it defines and the caller implements (10.1.3), so the dependency still points downward.

**RATIONALE**  A one-way dependency graph is what makes the layers independently comprehensible: you can read all of `core` without ever needing to know a GUI exists. The callback caveat is where this rule is usually violated in good faith — a progress callback looks like decoupling, but if `core` is written assuming something up there will paint a progress bar, the coupling is real and just invisible to the compiler.

**ENFORCEMENT**  CMake (actual gate) — a cycle in the target graph is a hard configure error, and `core` simply does not link `gui`. The callback case is Advisory — code review.

#### 10.1.3 core reports upward through interfaces it owns

**RULE**  When `core` must communicate with its caller mid-operation — progress reporting, cancellation checks, log sinks (13.4) — it declares a pure interface (3.18, 6.1.4) in `core`, accepts a non-owning pointer or reference to it, and calls through it. `gui` implements that interface, adapting to Qt signals on its own side. `core` never holds a `std::function` set from outside as its primary extension mechanism where an interface would do, and never assumes anything about who implements it.

**RATIONALE**  This is what keeps 10.1.2 honest while still allowing real communication. The interface belongs to `core` because `core` is the layer that knows what it needs to say; the adaptation to Qt's signal/slot world belongs to `gui` because that is the layer that knows Qt exists. Preferring an interface over a bare `std::function` is a readability call — a named interface with named methods documents the full protocol in one place, whereas four separately-set callbacks document nothing about how they relate or which are required.

**GOOD**

```cpp
// core/progress/iprogress_sink.h
class IProgressSink
{
public:
    virtual ~IProgressSink() = default;

    /**
     * @brief Reports that the given fraction of the current operation is complete.
     * @param fraction Completion in the range 0.0 to 1.0 inclusive.
     */
    virtual void reportProgress(double fraction) = 0;

    /**
     * @brief Indicates whether the caller has requested that the operation stop.
     * @return True if the operation should abandon its remaining work.
     */
    [[nodiscard]] virtual bool isCancelRequested() const = 0;
};

// core -- takes the interface, knows nothing about who implements it
std::expected<RecordBatch, Hdf5Error> readAll(IProgressSink* progress);
```

```cpp
// gui/progress/widget_progress_sink.h -- the Qt side lives here
class WidgetProgressSink : public QObject, public core::IProgressSink
{
    Q_OBJECT
public:
    void reportProgress(double fraction) override;   // emits a Qt signal
    [[nodiscard]] bool isCancelRequested() const override;
};
```

**BAD**

```cpp
// core/io/hdf5reader.h
#include "gui/progress/progress_dialog.h"           // BAD -- core including gui

std::expected<RecordBatch, Hdf5Error> readAll(gui::ProgressDialog* dialog);   // BAD -- core
                                                                              // now depends on a
                                                                              // specific widget
```

**ENFORCEMENT**  Advisory — code review, backed by the same grep as 10.1.1.

## 10.2 GUI architecture

#### 10.2.1 Model/View with a dedicated model layer; widgets contain no domain logic

**RULE**  `gui/` is organized in three directories with distinct responsibilities. `gui/models/` holds `QAbstractItemModel` subclasses that adapt `core` types for display — they own no domain logic, only presentation of data `core` produced. `gui/views/` holds widgets: layout, user input, rendering. `gui/controllers/` holds the objects that own a workflow — receiving user intent from a view, calling `core`, and updating models with the result. A widget subclass never calls `core` directly, never parses, never computes a derived value beyond what is needed to draw itself, and never owns a `core` object.

**RATIONALE**  Qt already provides a Model/View framework, and fighting it to install a different pattern (a full MVVM stack, say) means writing adapters for machinery Qt gives you. The addition worth making is the controller layer: without it, workflow logic has nowhere to live except inside widget subclasses, which is how a `MainWindow` becomes three thousand lines that cannot be tested without a display. Keeping widgets free of domain logic means the interesting behavior lives in objects that a test can construct — which is exactly what makes the QTest half of Section 12 tractable rather than an exercise in simulated mouse clicks.

**GOOD**

```cpp
// gui/controllers/import_controller.h -- owns the workflow
class ImportController : public QObject
{
    Q_OBJECT
public:
    void importFile(const std::filesystem::path& path);   // calls core, updates the model

signals:
    void importFailed(const QString& message);
};
```

```cpp
// gui/views/import_view.cpp -- forwards intent, displays results, decides nothing
void ImportView::onBrowseClicked()
{
    const QString selected = QFileDialog::getOpenFileName(this);
    controller->importFile(std::filesystem::path(selected.toStdString()));
}
```

**BAD**

```cpp
// gui/views/import_view.cpp
void ImportView::onBrowseClicked()
{
    const QString selected = QFileDialog::getOpenFileName(this);

    core::Hdf5Reader reader(selected.toStdString());      // BAD -- a widget calling core directly
    auto batch = reader.readBatch("primary");            // BAD -- workflow logic in a widget;
    if (!batch)                                           // untestable without a display
    {
        QMessageBox::critical(this, "Error", "Failed");
    }
}
```

**ENFORCEMENT**  Advisory — code review.

*Open item, needs team ratification: the three-directory split and the controller layer are a proposal, not an existing team decision. If the GUI is already structured differently, the useful question at review is not which pattern is better in the abstract but whether the current structure lets a workflow be tested without instantiating a window — that is the property this rule exists to buy.*

#### 10.2.2 Signals are past-tense facts; slots are imperative verbs

**RULE**  A signal is named for something that has already happened, in the past tense, with no `on` prefix and no `emit`-style verb: `batchLoaded`, `importFailed`, `selectionChanged`, `exportProgressed`. A slot is named as an ordinary member function per 3.7 — an imperative verb phrase describing what it does, not what triggered it: `refreshTable`, `showErrorMessage`, `cancelImport`. A slot is never named `onBatchLoaded` or `handleBatchLoaded`.

**RATIONALE**  The tense split is the whole point: a signal is an announcement that something is already true, and a slot is an instruction to do something. Naming them accordingly makes a `connect` line read as a sentence — "when the batch has loaded, refresh the table" — instead of "on batch loaded, on batch loaded." Rejecting the `on`/`handle` prefix on slots also keeps them consistent with every other member function in the codebase (3.7): a slot is an ordinary function that happens to be connectable, and naming it after its caller couples it to one connection when the same function is frequently useful from several.

**GOOD**

```cpp
class ImportController : public QObject
{
    Q_OBJECT

signals:
    void batchLoaded(const core::RecordBatch& batch);
    void importFailed(const QString& message);

public slots:
    void refreshTable();
    void showErrorMessage(const QString& message);
};

connect(controller, &ImportController::batchLoaded, view, &ImportView::refreshTable);
```

**BAD**

```cpp
signals:
    void loadBatch();               // BAD -- imperative; reads like a command, not an announcement
    void notifyImportFailure();     // BAD -- "notify" describes the mechanism, not the fact

public slots:
    void onBatchLoaded();           // BAD -- named after its caller; couples the slot to one
                                     // specific connection
```

**ENFORCEMENT**  Advisory — code review.

#### 10.2.3 Pointer-to-member connect syntax only; SIGNAL/SLOT macros are banned

**RULE**  Every `connect` call uses the pointer-to-member form: `connect(sender, &Sender::signalName, receiver, &Receiver::slotName)`. The string-based `SIGNAL()`/`SLOT()` macro form is never used. Where a lambda is connected instead of a member function, the connection passes a receiver `QObject*` as the third argument so the connection is destroyed with the receiver, and the lambda's captures are explicit per 6.1.11.

**RATIONALE**  This is 6.1.3's macro ban applied to Qt, and it earns its place on its own merits: `SIGNAL()`/`SLOT()` stringify their argument, so a typo, a changed signature, or a renamed signal produces no compile error at all — just a runtime warning on stderr and a connection that silently never fires. The pointer-to-member form is checked by the compiler, so the same mistakes become build errors. The receiver argument on lambda connections is the counterpart to 6.1.11's dangling-reference concern: without it, a lambda capturing `this` keeps being invoked after `this` is destroyed.

**GOOD**

```cpp
connect(controller, &ImportController::importFailed,
        view,       &ImportView::showErrorMessage);

// lambda form -- receiver passed, captures explicit
connect(controller, &ImportController::batchLoaded, this,
        [this](const core::RecordBatch& batch) { updateRowCount(batch.size()); });
```

**BAD**

```cpp
connect(controller, SIGNAL(importFailed(QString)),      // BAD -- macro form; a signature typo
        view, SLOT(showErrorMessage(QString)));          // fails silently at runtime

connect(controller, &ImportController::batchLoaded,      // BAD -- no receiver; the lambda
        [this](const core::RecordBatch& b) { /* ... */ });  // outlives `this`
```

**ENFORCEMENT**  Compiler (actual gate) for signature correctness once the pointer-to-member form is used. `QT_NO_KEYWORDS`-style enforcement of the macro ban is Advisory — code review, plus a grep for `SIGNAL(` listed in Section 7.

## 10.3 API stability

#### 10.3.1 core has no stability guarantee before 1.0; breaking changes are marked, not avoided

**RULE**  While the version stays at 0.y.z (2.1), `core`'s API carries no compatibility promise. A breaking change to a `core` interface is made directly, in one commit, with the `!` marker and `BREAKING CHANGE:` footer required by 1.3.3 — it is not worked around with an overload, a shim, or a parallel v2 API. All in-tree callers are updated in the same commit. There is no deprecation period, because there is no external consumer to give notice to.

**RATIONALE**  Deprecation machinery costs something real: every deprecated function is a second code path to keep working, test, and read past. That cost is worth paying when you have consumers who cannot be updated on your schedule — and pre-1.0, with `core` consumed only by `gui` and `app` in the same repository, there are none. Changing the interface and its callers together is strictly cheaper and leaves no residue. The `!` marker still matters because the changelog and the version derivation both read it (2.1).

**ENFORCEMENT**  Advisory — code review; the `!`/footer requirement is enforced as part of 1.3.3.

#### 10.3.2 After 1.0: one release of deprecation before removal

**RULE**  Once the project reaches 1.0, a public `core` symbol is removed only after it has shipped in at least one tagged release marked `[[deprecated("...")]]` with a message naming the replacement. The deprecation is announced in that release's changelog entry. This rule takes effect at 1.0 and not before; until then, 10.3.1 applies.

**RATIONALE**  Written now rather than at 1.0 because the point at which this becomes necessary is the point at which it is most likely to be skipped — 1.0 is cut under schedule pressure and nobody stops to design a deprecation policy. The `[[deprecated]]` attribute is the right mechanism because it produces a compiler warning at every call site, which under 9.2.2's warnings-as-errors policy makes an internal caller a build failure while remaining a mere warning for anyone outside.

**GOOD**

```cpp
[[deprecated("Use readBatch(std::string_view) instead; removed in 2.0.")]]
std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
```

**ENFORCEMENT**  Compiler warning (real gate under 9.2.2 for in-tree callers); Advisory — code review that the deprecation shipped in a release before removal.

## 10.4 Ownership

#### 10.4.1 Module ownership is documented, advisory, and never a merge gate

**RULE**  A table in this document (below) names a primary and a secondary familiar developer for each top-level module. Ownership means: first person to ask, expected reviewer for a substantial change, responsible for keeping that module's section of this guide accurate. It does not mean approval authority — 1.7.1's rule that any team member may approve any PR is unchanged, and no CODEOWNERS file is introduced.

**RATIONALE**  The value here is routing, not gatekeeping: on a small rotating team the expensive failure is not an unreviewed change, it is a change that sat for two days because nobody knew who to ask about the HDF5 layer. Naming a person answers that instantly. Making it a merge gate would work directly against 1.7.1 and would turn a single person's vacation into a blocked queue, which is the exact bus-factor risk 2.3.1 already argues against.

| Module | Primary | Secondary |
| --- | --- | --- |
| core/io (HDF5, zip, file formats) | *unassigned* | *unassigned* |
| core/analysis | *unassigned* | *unassigned* |
| gui/models, gui/views | *unassigned* | *unassigned* |
| gui/visualization (Vulkan) | *unassigned* | *unassigned* |
| app (CLI, bootstrap) | *unassigned* | *unassigned* |
| Build system (CMake, vcpkg, presets) | *unassigned* | *unassigned* |
| This guide | *unassigned* | *unassigned* |

*Open item, needs team ratification: the module breakdown is inferred from the directory structure described in Section 8 and the libraries named on the master topic list — confirm it matches the real tree. Every name is deliberately left unassigned; filling them in is a team decision, and an ownership table with guessed names is worse than none.*

**ENFORCEMENT**  Advisory — the table is a routing aid, deliberately not wired to any gate.
