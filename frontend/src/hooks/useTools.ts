import { useEffect, useState } from 'react';
import { getTools } from '../api/client';
import { ToolDefinition } from '../api/types';

export function useTools() {
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getTools()
      .then((data) => {
        if (mounted) setTools(data);
      })
      .catch((err) => {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch tools.');
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return { tools, loading, error };
}
