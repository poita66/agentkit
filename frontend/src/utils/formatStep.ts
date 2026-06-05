import { ToolDefinition } from '../api/types';

interface Step {
  tool_name: string | null;
  args: Record<string, unknown> | null;
  result: Record<string, unknown>;
}

const TEMPLATE_DESCRIPTIONS: Record<string, (args: Record<string, unknown> | null) => string> = {
  search_docs: (args) => `Searching documentation for "${args?.query ?? 'information'}"`,
  search_web: (args) => `Searching the web for "${args?.query ?? 'information'}"`,
  read_file: (args) => `Reading file "${args?.path ?? 'unknown'}"`,
  write_file: (args) => `Writing file "${args?.path ?? 'unknown'}"`,
  calculate: (args) => `Calculating "${args?.expression ?? 'an expression'}"`,
  summarize: (args) => `Summarizing text`,
  translate: (args) => `Translating to ${args?.target_language ?? 'another language'}`,
  query_database: (args) => `Querying database for "${args?.query ?? 'data'}"`,
  send_email: (args) => `Sending email to ${args?.to ?? 'a recipient'}`,
  list_files: (args) => `Listing files in "${args?.path ?? 'a directory'}"`,
};

function describeToolCall(toolName: string, args: Record<string, unknown> | null, tools: ToolDefinition[]): string {
  const tool = tools.find((t) => t.name === toolName);
  if (tool) {
    const desc = tool.description;
    const query = args?.query as string | undefined;
    const path = args?.path as string | undefined;
    const expression = args?.expression as string | undefined;
    const target_language = args?.target_language as string | undefined;
    const to = args?.to as string | undefined;

    if (query) return `${desc}: "${query}"`;
    if (path) return `${desc}: "${path}"`;
    if (expression) return `${desc}: "${expression}"`;
    if (target_language) return `${desc}: ${target_language}`;
    if (to) return `${desc}: ${to}`;
    return desc;
  }

  const template = TEMPLATE_DESCRIPTIONS[toolName];
  if (template) {
    return template(args);
  }

  return `Using ${toolName}`;
}

export function describeStep(step: Step, tools: ToolDefinition[] = []): string {
  if (step.tool_name === null) {
    const answer = step.result?.answer as string | undefined;
    return answer ?? 'Final answer';
  }

  return describeToolCall(step.tool_name, step.args, tools);
}
