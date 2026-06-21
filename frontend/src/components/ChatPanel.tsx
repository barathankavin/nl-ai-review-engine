import { useEffect, useState } from 'react';
import { fetchChatStatus, sendChatQuery } from '../lib/api';
import { formatChatAnswer } from '../lib/chatFormat';

interface ChatMessage {
  role: 'user' | 'assistant';
  body?: string;
  citations?: string[];
  citationsValid?: boolean;
  content?: string;
}

const DEFAULT_QUESTIONS = [
  'Why do users struggle to discover new music?',
  'What are the most common frustrations with recommendations?',
  'What listening behaviors are users trying to achieve?',
  'What causes users to repeatedly listen to the same content?',
  'Which user segments experience different discovery challenges?',
  'What unmet needs emerge consistently across reviews?',
];

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      body:
        'Ask about discovery, recommendations, and listening behavior. Answers are concise and grounded in your review data.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [groqEnabled, setGroqEnabled] = useState(false);
  const [groqModel, setGroqModel] = useState<string | null>(null);
  const [sampleQuestions, setSampleQuestions] = useState(DEFAULT_QUESTIONS);

  useEffect(() => {
    void fetchChatStatus()
      .then((status) => {
        setGroqEnabled(status.groq_enabled);
        setGroqModel(status.groq_model);
        if (status.sample_questions.length > 0) {
          setSampleQuestions(status.sample_questions);
        }
      })
      .catch(() => setGroqEnabled(false));
  }, []);

  const ask = async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || loading) return;

    setInput('');
    setMessages((current) => [...current, { role: 'user', content: trimmed }]);
    setLoading(true);

    try {
      const response = await sendChatQuery(trimmed);
      setGroqEnabled(response.groq_enabled);
      const formatted = formatChatAnswer(response.answer, response.citations);
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          body: formatted.body,
          citations: formatted.citations,
          citationsValid: response.citations_valid,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          body: error instanceof Error ? error.message : 'Chat request failed.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="chat-panel">
      <div className="chat-panel__header">
        <div>
          <h2 className="section-title">Discovery chat</h2>
          <p className="section-subtitle">Groq analysis · short cited sources</p>
        </div>
        <span className={`pill ${groqEnabled ? 'pill--online' : 'pill--offline'}`}>
          {groqEnabled ? `Groq · ${groqModel ?? 'ready'}` : 'Groq not configured'}
        </span>
      </div>

      {!groqEnabled && (
        <p className="chat-panel__notice">
          Add <code>GROQ_API_KEY</code> to <code>backend/.env</code> and restart the backend.
        </p>
      )}

      <div className="chat-panel__suggestions">
        {sampleQuestions.slice(0, 4).map((question) => (
          <button
            key={question}
            type="button"
            className="chip"
            onClick={() => void ask(question)}
            disabled={loading}
          >
            {question}
          </button>
        ))}
      </div>

      <div className="chat-panel__messages">
        {messages.map((message, index) => (
          <article
            key={`${message.role}-${index}`}
            className={`chat-message chat-message--${message.role}`}
          >
            {message.role === 'user' ? (
              <p>{message.content}</p>
            ) : (
              <>
                <p className="chat-message__answer">{message.body ?? message.content}</p>
                {message.citations && message.citations.length > 0 && (
                  <div className="chat-message__sources">
                    <span>Sources</span>
                    {message.citations.map((id) => (
                      <code key={id} title={id}>
                        {id}
                      </code>
                    ))}
                    {message.citationsValid === false ? (
                      <em className="chat-message__verify">partially verified</em>
                    ) : null}
                  </div>
                )}
              </>
            )}
          </article>
        ))}
      </div>

      <form
        className="chat-panel__composer"
        onSubmit={(event) => {
          event.preventDefault();
          void ask(input);
        }}
      >
        <input
          type="text"
          placeholder="Why do users struggle to discover new music?"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? 'Analyzing…' : 'Ask'}
        </button>
      </form>
    </section>
  );
}
