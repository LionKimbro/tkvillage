We are making the following application:

TkVillage is a lightweight importable Python/Tkinter runtime for building modular GUI applications around a hidden root, summonable Toplevel windows, reducer-powered state dictionaries, queued semantic events, and a periodic tick loop. It provides the shared “host organism” for Lion-style Tkinter apps: window kind registration, singleton/per-key/free-instance window policies, target queues for windows and services, message routing, configuration, lifecycle hooks, testing support, and debug/introspection tools. The goal is not to build CIRA, a visual builder, or a heavy framework, but a small inspectable kernel that makes Tkinter programs reusable, AI-debuggable, and consistent with lions-tkinter-development-conventions.v1.

Below are reference documents, grouped by when to read them. Each entry includes both its Librarian registry ID and its resolved full path.

Read now (before you begin):

- Lion's Dictionary for LLMs — Abbreviated
  Registry ID: lions_dictionary_for_llms.abbreviated.v1
  Path: C:\lion\github\lions-documents\raw\0009__lions-dictionary-for-llms_abbreviated.json
  Why: Read this for an abbreviated high-level orientation to Lion's recurring concepts, systems, and vocabulary.

- Lion's Python Programming Guidelines (2025) -- Simplified Edition
  Registry ID: lionsphilosophyofprogramming.2025.simplified
  Path: C:\lion\github\lions-documents\coding-guidelines\v2026-01-14_part2_lions-philosophy-of-programming_simplified.json
  Why: These are the programming guidelines that you shall implement the program with.

- lionscliapp Reference Guide
  Registry ID: lionscliapp.reference.v1
  Path: C:\lion\github\lionscliapp\doc\reference.json
  Why: TkVillage core must not REQUIRE lionscliapp, but TkVillage should provides a standard lionscliapp integration path because I estimate 80%-95% of use will be atop lionscliapp.

- Lion's Tkinter Development Conventions
  Registry ID: lions-tkinter-development-conventions.v1
  Path: C:\lion\github\lions-documents\raw\0010__lions-tkinter-development-conventions_v1.json
  Why: These are tkinter development conventions, and the framework we are now implementing in many ways is a reification of these principles.

- CIRA Agentic Implementation Brief
  Registry ID: cira.agentic-implementation-brief.v1
  Path: C:\lion\github\reducer-core-architecture\docs\raw\0004__cira_agentic-implementation-brief.json
  Why: Typically, we will use reducer-core architecture, per program spec.  However, there will be references to CIRA, and some times, especially if a tkinter.Toplevel makes heavy use of a tkinter.Canvas, -- the full CIRA will be used.  CIRA stands for Coordinated Interactive Runtime Architecture (CIRA). Read this so that you have an idea of what is coming for those instances.

Read when relevant (do not read these yet):
Note that these exist and what each one covers, but do not read them now. Open a document only when you are about to do work that requires its knowledge.

- Minimal JSON Document Format for LLMs
  Registry ID: lions-docs.description.json-document-format-for-llms.minimal.v1
  Path: C:\lion\github\lions-documents\raw\0002__lions-docs-description_json-document-for-llms_simplified_v1.json
  Why: A condensed version of the JSON documentation-writing guide; read this for the essentials when the full guide is more than you need.

- SoftSpec Specification (v2)
  Registry ID: softspec.spec.v2
  Path: C:\lion\github\soft-schema\docs\raw\02__second-pass.txt
  Why: Read this when specifying data structures in JSON documents; SoftSpec is the preferred approach.

- MachineRoot Python Package Description
  Registry ID: machine-root.package.description.v1
  Path: C:\lion\github\machine-root\docs\raw\0001__machineroot-package.json
  Why: "Machine Root" is something like an environment variable system, except rather than being tied to the process, it refers to system-wide variables, and they are programmatically accessible.

Please acknowledge which documents you read before beginning implementation.

If you find a blocking ambiguity, ask before making a consequential assumption. If the ambiguity is minor and the TkVillage Kernel Specification gives enough direction, make the simplest implementation-consistent choice and continue.

Important implementation boundary: build the minimum viable TkVillage kernel first. Do not expand into full CIRA, a visual builder, tutorial overlays, a full plugin system, a game engine, or a heavy framework unless explicitly instructed.
