# Suvyon Project Explorer

An interactive, dependency-free learning tool for tracing the real Suvyon implementation from frontend entry point through APIs, services, persistence, RAG, agents, tools, and LLM providers.

## Open it

From the repository root:

```powershell
python -m http.server 4173
```

Then open:

```text
http://localhost:4173/interview-prep/project-explorer/
```

The tool also works by opening `index.html` directly, but serving the repository is more reliable across browsers.

## Study method

1. Read one chapter's plain-language explanation.
2. Follow its flow chart from left to right.
3. Open every linked source location.
4. Answer the interview checks without notes.
5. Mark the chapter complete only when you can explain input, processing, output, security boundary, failure modes, and production gap.

Source buttons target the repository's `Interview-Prep` branch and include exact line anchors.
