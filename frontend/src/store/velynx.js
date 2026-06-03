import { create } from 'zustand';

export const useVelynxStore = create(() => ({
  lastQuery: '',
  setLastQuery: () => {},
}));
