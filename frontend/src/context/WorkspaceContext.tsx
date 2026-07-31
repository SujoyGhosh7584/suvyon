import { createContext, useContext, useMemo, useState } from "react";

type WorkspaceContextValue = {
  workspaceId: string | null;
  setWorkspaceId: (id: string | null) => void;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);
const STORAGE_KEY = "suvyon_workspace_id";

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [workspaceId, setWorkspaceIdState] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY),
  );

  const setWorkspaceId = (id: string | null) => {
    setWorkspaceIdState(id);
    if (id) localStorage.setItem(STORAGE_KEY, id);
    else localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo(
    () => ({ workspaceId, setWorkspaceId }),
    [workspaceId],
  );

  return (
    <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
