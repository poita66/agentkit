import { describe, it, expect } from 'vitest';
import { describeStep } from '@/utils/formatStep';

describe('describeStep', () => {
  it('returns final answer for null tool_name with data', () => {
    const step = { tool_name: null, args: null, result: { ok: true, data: 'The answer is 42' } };
    expect(describeStep(step)).toBe('The answer is 42');
  });

  it('returns generic final answer for null tool_name without data', () => {
    const step = { tool_name: null, args: null, result: { ok: true } };
    expect(describeStep(step)).toBe('Final answer');
  });

  it('describes search_documents with query', () => {
    const step = { tool_name: 'search_documents', args: { query: 'Q3 report' }, result: { ok: true, data: 'found' } };
    expect(describeStep(step)).toBe('Searching documents for "Q3 report"');
  });

  it('describes search_documents with fallback query', () => {
    const step = { tool_name: 'search_documents', args: null, result: { ok: true } };
    expect(describeStep(step)).toBe('Searching documents for "information"');
  });

  it('describes read_file with path', () => {
    const step = { tool_name: 'read_file', args: { path: '/docs/report.txt' }, result: { ok: true, data: 'content' } };
    expect(describeStep(step)).toBe('Reading file "/docs/report.txt"');
  });

  it('describes write_file with path', () => {
    const step = { tool_name: 'write_file', args: { path: '/docs/output.txt' }, result: { ok: true } };
    expect(describeStep(step)).toBe('Writing file "/docs/output.txt"');
  });

  it('describes execute_code generically', () => {
    const step = { tool_name: 'execute_code', args: { code: 'print(1)' }, result: { ok: true } };
    expect(describeStep(step)).toBe('Executing code');
  });

  it('describes search_web with query', () => {
    const step = { tool_name: 'search_web', args: { query: 'latest news' }, result: { ok: true } };
    expect(describeStep(step)).toBe('Searching the web for "latest news"');
  });

  it('describes read_url with url', () => {
    const step = { tool_name: 'read_url', args: { url: 'https://example.com' }, result: { ok: true } };
    expect(describeStep(step)).toBe('Reading "https://example.com"');
  });

  it('falls back to generic message for unknown tool', () => {
    const step = { tool_name: 'unknown_tool', args: null, result: { ok: true } };
    expect(describeStep(step)).toBe('Using unknown_tool');
  });
});
