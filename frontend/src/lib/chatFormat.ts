export function formatChatAnswer(raw: string, citations: string[] = []) {
  const sourcesMatch = raw.match(/\n*Sources?:\s*(.+)$/i);
  let body = raw;
  let parsedCitations = [...citations];

  if (sourcesMatch) {
    body = raw.slice(0, sourcesMatch.index).trim();
    const ids = sourcesMatch[1]
      .split(/[,;]\s*/)
      .map((part) => part.replace(/^review\s*#?/i, '').trim())
      .filter(Boolean);
    if (ids.length > 0) {
      parsedCitations = ids;
    }
  }

  body = body
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/review\s*#([0-9a-fA-F-]+)/gi, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  const shortCitations = parsedCitations.map((id) => id.slice(0, 8));

  return { body, citations: shortCitations };
}
