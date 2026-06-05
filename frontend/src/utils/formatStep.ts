interface Step {
  tool_name: string | null;
  args: Record<string, unknown> | null;
  result: Record<string, unknown>;
}

const TOOL_DESCRIPTIONS: Record<string, (args: Record<string, unknown> | null) => string> = {
  search_documents: (args) => `Searching documents for "${args?.query ?? 'information'}"`,
  read_file: (args) => `Reading file "${args?.path ?? 'unknown'}"`,
  write_file: (args) => `Writing file "${args?.path ?? 'unknown'}"`,
  execute_code: () => 'Executing code',
  search_web: (args) => `Searching the web for "${args?.query ?? 'information'}"`,
  read_url: (args) => `Reading "${args?.url ?? 'a webpage'}"`,
};

export function describeStep(step: Step): string {
  if (step.tool_name === null) {
    const data = step.result?.data as string | undefined;
    return data ?? 'Final answer';
  }

  const descriptor = TOOL_DESCRIPTIONS[step.tool_name];
  if (descriptor) {
    return descriptor(step.args);
  }

  return `Using ${step.tool_name}`;
}
