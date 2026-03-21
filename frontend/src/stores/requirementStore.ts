import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Requirement } from '@/types'

export interface RequirementState {
  requirements: Requirement[]
  selectedRequirement: Requirement | null
  isLoading: boolean
  error: string | null

  setRequirements: (requirements: Requirement[]) => void
  addRequirement: (requirement: Requirement) => void
  updateRequirement: (id: string, updates: Partial<Requirement>) => void
  removeRequirement: (id: string) => void
  selectRequirement: (requirement: Requirement | null) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
}

export const useRequirementStore = create<RequirementState>()(
  persist(
    (set) => ({
      requirements: [],
      selectedRequirement: null,
      isLoading: false,
      error: null,

      setRequirements: (requirements) => set({ requirements }),

      addRequirement: (requirement) =>
        set((state) => ({
          requirements: [...state.requirements, requirement],
        })),

      updateRequirement: (id, updates) =>
        set((state) => ({
          requirements: state.requirements.map((req) =>
            req.id === id ? { ...req, ...updates } : req
          ),
          selectedRequirement:
            state.selectedRequirement?.id === id
              ? { ...state.selectedRequirement, ...updates }
              : state.selectedRequirement,
        })),

      removeRequirement: (id) =>
        set((state) => ({
          requirements: state.requirements.filter((req) => req.id !== id),
          selectedRequirement:
            state.selectedRequirement?.id === id ? null : state.selectedRequirement,
        })),

      selectRequirement: (requirement) =>
        set({ selectedRequirement: requirement }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),
    }),
    {
      name: 'requirement-storage',
      partialize: (state) => ({
        requirements: state.requirements,
        selectedRequirement: state.selectedRequirement,
      }),
    }
  )
)

// Decomposition state
export interface SubRequirement {
  id: string
  title: string
  description: string
  priority: number
  complexity: number
  estimated_hours: number
  dependencies: string[]
}

export interface DecompositionResult {
  requirement_id: string
  complexity: number
  estimated_total_hours: number
  sub_requirements: SubRequirement[]
  tasks: Array<{
    id: string
    title: string
    description: string
    requirement_id: string
    project_id: string
    priority: number
    task_type: string
    estimated_hours: number
    sort_order: number
    dependencies: string[]
  }>
  validation: {
    status: 'valid' | 'has_warnings' | 'invalid'
    conflicts: Array<{ type: string; severity: string; message: string }>
    warnings: string[]
    suggestions: string[]
  }
}

interface DecompositionState {
  currentDecomposition: DecompositionResult | null
  isDecomposing: boolean
  decompositionError: string | null

  setDecomposition: (result: DecompositionResult | null) => void
  setDecomposing: (isDecomposing: boolean) => void
  setDecompositionError: (error: string | null) => void
  clearDecomposition: () => void
}

export const useDecompositionStore = create<DecompositionState>()((set) => ({
  currentDecomposition: null,
  isDecomposing: false,
  decompositionError: null,

  setDecomposition: (result) => set({ currentDecomposition: result }),
  setDecomposing: (isDecomposing) => set({ isDecomposing }),
  setDecompositionError: (error) => set({ decompositionError: error }),
  clearDecomposition: () =>
    set({
      currentDecomposition: null,
      isDecomposing: false,
      decompositionError: null,
    }),
}))
