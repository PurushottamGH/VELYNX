import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar.jsx';
import Pipeline from './components/Pipeline.jsx';
import { postQuery } from './api/velynx.js';
import { useChatStore } from './store/velynx.js';

export default function App() {
  const [queryText, setQueryText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { addUserMessage, addAssistantMessage, messages } = useChatStore();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!queryText.trim() || isLoading) return;
    
    const normalized = queryText.trim();
    setQueryText('');
    setIsLoading(true);
    
    // Add user message immediately
    addUserMessage(normalized);
    
    try {
      const response = await postQuery({ text: normalized });
      addAssistantMessage(response);
    } catch (error) {
      console.error('Query failed:', error);
      addAssistantMessage({
        answer: 'Error: Failed to get response from server.',
        confidence: 'LOW',
        resonance_scores: {},
        epistemic_states: {},
        recalled_memory: null
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-black">
      <Pipeline />
    </div>
  );
}