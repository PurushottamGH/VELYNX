import { create } from 'zustand';

export const useVelynxStore = create((set, get) => ({
  messages: [],
  lastQuery: '',
  setLastQuery: (query) => set({ lastQuery: query }),
  
  addUserMessage: (content) => {
    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      telemetry: null
    };
    set((state) => ({ messages: [...state.messages, userMessage] }));
  },
  
  addAssistantMessage: (response) => {
    const assistantMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: response.answer,
      telemetry: {
        resonanceScores: response.resonance_scores || {},
        epistemicStates: response.epistemic_states || {},
        recalledMemory: response.recalled_memory || null
      }
    };
    set((state) => ({ messages: [...state.messages, assistantMessage] }));
  },
  
  clearMessages: () => set({ messages: [] }),
}));

export const useChatStore = create((set, get) => ({
  messages: [],
  
  addUserMessage: (content) => {
    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      telemetry: null
    };
    set((state) => ({ messages: [...state.messages, userMessage] }));
  },
  
  addAssistantMessage: (response) => {
    const assistantMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: response.answer,
      telemetry: {
        resonanceScores: response.resonance_scores || {},
        epistemicStates: response.epistemic_states || {},
        recalledMemory: response.recalled_memory || null
      }
    };
    set((state) => ({ messages: [...state.messages, assistantMessage] }));
  },
  
  clearMessages: () => set({ messages: [] }),
}));