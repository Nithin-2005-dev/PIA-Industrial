import { create } from 'zustand';

export interface WorkspaceConfig {
  id: string;
  name: string;
  dataset: string;
  repository: string; // Internal alias for workspace id
}

interface WorkspaceState {
  workspace: WorkspaceConfig;
  updateWorkspace: (updates: Partial<WorkspaceConfig>) => void;
  setActiveWorkspace: (id: string, name: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspace: {
    id: 'demo-p101',
    name: 'P-101 Demo Plant',
    dataset: 'P-101 Demo Dataset',
    repository: 'demo-p101',
  },
  updateWorkspace: (updates) => set((state) => ({ 
    workspace: { ...state.workspace, ...updates } 
  })),
  setActiveWorkspace: (id, name) => set((state) => ({
    workspace: { ...state.workspace, id, name, repository: id, dataset: name },
  })),
}));

