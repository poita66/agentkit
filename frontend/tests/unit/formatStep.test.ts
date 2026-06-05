import { describe, it, expect } from 'vitest';
import { describeStep } from '@/utils/formatStep';
import { ToolDefinition } from '@/api/types';

const mockTools: ToolDefinition[] = [
  { name: 'search_docs', description: 'Search documentation and knowledge base for relevant information', parameters: {} },
  { name: 'search_web', description: 'Search the web for current information and news', parameters: {} },
  { name: 'read_file', description: 'Read the contents of a file from the filesystem', parameters: {} },
  { name: 'write_file', description: 'Write content to a file on the filesystem', parameters: {} },
  { name: 'calculate', description: 'Perform mathematical calculations and computations', parameters: {} },
  { name: 'summarize', description: 'Summarize text content into key points', parameters: {} },
  { name: 'translate', description: 'Translate text between languages', parameters: {} },
  { name: 'query_database', description: 'Query a database for structured data', parameters: {} },
  { name: 'send_email', description: 'Send an email message to a recipient', parameters: {} },
  { name: 'list_files', description: 'List files and directories in a given path', parameters: {} },
];

describe('describeStep', () => {
  it('returns final answer for null tool_name with data', () => {
    const step = { tool_name: null, args: null, result: { ok: true, data: 'The answer is 42' } };
    expect(describeStep(step)).toBe('The answer is 42');
  });

  it('returns generic final answer for null tool_name without data', () => {
    const step = { tool_name: null, args: null, result: { ok: true } };
    expect(describeStep(step)).toBe('Final answer');
  });

  describe('with API tool definitions', () => {
    it('describes search_docs with query from API description', () => {
      const step = { tool_name: 'search_docs', args: { query: 'Q3 report' }, result: { ok: true, data: 'found' } };
      expect(describeStep(step, mockTools)).toBe('Search documentation and knowledge base for relevant information: "Q3 report"');
    });

    it('describes search_web with query from API description', () => {
      const step = { tool_name: 'search_web', args: { query: 'latest news' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Search the web for current information and news: "latest news"');
    });

    it('describes read_file with path from API description', () => {
      const step = { tool_name: 'read_file', args: { path: '/docs/report.txt' }, result: { ok: true, data: 'content' } };
      expect(describeStep(step, mockTools)).toBe('Read the contents of a file from the filesystem: "/docs/report.txt"');
    });

    it('describes write_file with path from API description', () => {
      const step = { tool_name: 'write_file', args: { path: '/docs/output.txt' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Write content to a file on the filesystem: "/docs/output.txt"');
    });

    it('describes calculate with expression from API description', () => {
      const step = { tool_name: 'calculate', args: { expression: '2 + 2' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Perform mathematical calculations and computations: "2 + 2"');
    });

    it('describes summarize from API description', () => {
      const step = { tool_name: 'summarize', args: { text: 'some text' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Summarize text content into key points');
    });

    it('describes translate with target language from API description', () => {
      const step = { tool_name: 'translate', args: { text: 'hello', target_language: 'French' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Translate text between languages: French');
    });

    it('describes query_database with query from API description', () => {
      const step = { tool_name: 'query_database', args: { query: 'SELECT * FROM users' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Query a database for structured data: "SELECT * FROM users"');
    });

    it('describes send_email with recipient from API description', () => {
      const step = { tool_name: 'send_email', args: { to: 'user@example.com', subject: 'Hi', body: 'Hello' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Send an email message to a recipient: user@example.com');
    });

    it('describes list_files with path from API description', () => {
      const step = { tool_name: 'list_files', args: { path: '/docs' }, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('List files and directories in a given path: "/docs"');
    });

    it('describes tool with no relevant args from API description', () => {
      const step = { tool_name: 'summarize', args: null, result: { ok: true } };
      expect(describeStep(step, mockTools)).toBe('Summarize text content into key points');
    });
  });

  describe('fallback to template descriptions', () => {
    it('describes search_docs with query from template', () => {
      const step = { tool_name: 'search_docs', args: { query: 'Q3 report' }, result: { ok: true, data: 'found' } };
      expect(describeStep(step, [])).toBe('Searching documentation for "Q3 report"');
    });

    it('describes search_docs with fallback query from template', () => {
      const step = { tool_name: 'search_docs', args: null, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Searching documentation for "information"');
    });

    it('describes search_web with query from template', () => {
      const step = { tool_name: 'search_web', args: { query: 'latest news' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Searching the web for "latest news"');
    });

    it('describes read_file with path from template', () => {
      const step = { tool_name: 'read_file', args: { path: '/docs/report.txt' }, result: { ok: true, data: 'content' } };
      expect(describeStep(step, [])).toBe('Reading file "/docs/report.txt"');
    });

    it('describes write_file with path from template', () => {
      const step = { tool_name: 'write_file', args: { path: '/docs/output.txt' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Writing file "/docs/output.txt"');
    });

    it('describes calculate with expression from template', () => {
      const step = { tool_name: 'calculate', args: { expression: '2 + 2' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Calculating "2 + 2"');
    });

    it('describes summarize from template', () => {
      const step = { tool_name: 'summarize', args: { text: 'some text' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Summarizing text');
    });

    it('describes translate with target language from template', () => {
      const step = { tool_name: 'translate', args: { text: 'hello', target_language: 'French' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Translating to French');
    });

    it('describes query_database with query from template', () => {
      const step = { tool_name: 'query_database', args: { query: 'SELECT * FROM users' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Querying database for "SELECT * FROM users"');
    });

    it('describes send_email with recipient from template', () => {
      const step = { tool_name: 'send_email', args: { to: 'user@example.com', subject: 'Hi', body: 'Hello' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Sending email to user@example.com');
    });

    it('describes list_files with path from template', () => {
      const step = { tool_name: 'list_files', args: { path: '/docs' }, result: { ok: true } };
      expect(describeStep(step, [])).toBe('Listing files in "/docs"');
    });
  });

  it('falls back to generic message for unknown tool', () => {
    const step = { tool_name: 'unknown_tool', args: null, result: { ok: true } };
    expect(describeStep(step, mockTools)).toBe('Using unknown_tool');
  });
});
