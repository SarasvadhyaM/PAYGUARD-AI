import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, NavLink, Route, Routes } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const sampleMessages = [
  'URGENT: Your UPI account is suspended. Pay ₹999 to reactivate or send OTP immediately.',
  'Congratulations! You won a cashback of ₹2,000. Click this link to claim it right now.',
  'Your electricity bill is due by 5 PM today. Please pay the bill using the secure link below.'
];

function App() {
  return (
    <div className="page-shell">
      <Header />
      <main className="content-wrap">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/scam-analyzer" element={<ScamAnalyzerPage />} />
          <Route path="/payment-checker" element={<PaymentCheckerPage />} />
          <Route path="/safety-assistant" element={<SafetyAssistantPage />} />
          <Route path="/learn-safety" element={<LearnSafetyPage />} />
        </Routes>
      </main>
    </div>
  );
}

function Header() {
  const [language, setLanguage] = useState('en');
  return (
    <header className="topbar">
      <div className="brand-block">
        <Link to="/" className="brand">
          <span className="brand-mark">P</span>
          <span>PayGuard AI</span>
        </Link>
      </div>
      <nav className="primary-nav" aria-label="Main navigation">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/scam-analyzer">Scam Analyzer</NavLink>
        <NavLink to="/payment-checker">Payment Checker</NavLink>
        <NavLink to="/safety-assistant">Safety Assistant</NavLink>
        <NavLink to="/learn-safety">Learn Safety</NavLink>
      </nav>
      <label className="language-picker" aria-label="Choose language">
        <span>Language</span>
        <select value={language} onChange={(event) => setLanguage(event.target.value)}>
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
          <option value="mr">मराठी</option>
        </select>
      </label>
    </header>
  );
}

function HomePage() {
  const cards = [
    { title: 'Scam Analyzer', path: '/scam-analyzer', text: 'Paste messages and identify warning signs before paying.' },
    { title: 'Payment Checker', path: '/payment-checker', text: 'Verify amount mismatches and missing recipient details.' },
    { title: 'Safety Assistant', path: '/safety-assistant', text: 'Ask safe-payment questions in simple language.' },
    { title: 'Learn Safety', path: '/learn-safety', text: 'Practice five common scam scenarios and improve confidence.' }
  ];

  return (
    <section className="home-page">
      <div className="hero-card">
        <p className="eyebrow">Pause. Understand. Verify. Pay Safely.</p>
        <h1>PayGuard AI</h1>
        <p className="lead">Your intelligent assistant for safer digital payments.</p>
        <div className="cta-row">
          <Link className="primary-btn" to="/scam-analyzer">Check a message</Link>
          <Link className="secondary-btn" to="/payment-checker">Verify a payment</Link>
        </div>
      </div>
      <div className="card-grid">
        {cards.map((card) => (
          <Link key={card.title} to={card.path} className="feature-card">
            <h2>{card.title}</h2>
            <p>{card.text}</p>
            <span className="card-link">Open</span>
          </Link>
        ))}
      </div>
    </section>
  );
}

function ScamAnalyzerPage() {
  const [message, setMessage] = useState(sampleMessages[0]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submitMessage = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/api/analyze-message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(payload.detail || 'Unable to analyze the message.');
      }
      setResult(payload);
    } catch (err) {
      setError(err.message || 'Could not analyze the message.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const riskClass = useMemo(() => {
    if (!result) return '';
    if (result.risk_category === 'High Concern') return 'risk-pill high';
    if (result.risk_category === 'Needs Verification') return 'risk-pill medium';
    return 'risk-pill low';
  }, [result]);

  return (
    <section className="panel-page">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Scam Analyzer</p>
          <h2>Check suspicious payment messages</h2>
        </div>
      </div>
      <div className="panel-body">
        <label htmlFor="payment-message" className="field-label">Paste the message</label>
        <textarea
          id="payment-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows="6"
          maxLength={600}
          placeholder="Paste a suspicious message, SMS, or WhatsApp text here"
        />
        <div className="sample-row">
          {sampleMessages.map((sample) => (
            <button key={sample} type="button" className="tiny-btn" onClick={() => setMessage(sample)}>
              Load example
            </button>
          ))}
        </div>
        <div className="button-row">
          <button type="button" className="primary-btn" onClick={submitMessage} disabled={loading || !message.trim()}>
            {loading ? 'Checking…' : 'Analyze Message'}
          </button>
          <button type="button" className="secondary-btn" onClick={() => { setMessage(''); setResult(null); setError(''); }}>
            Clear
          </button>
        </div>

        {error && <div className="status-box error-box"><strong>Error:</strong> {error}</div>}

        {!result && !error && !loading && (
          <div className="empty-state">No message checked yet. Paste a message to see scam indicators.</div>
        )}

        {result && (
          <div className="result-box">
            <div className="result-header">
              <h3>Assessment</h3>
              <span className={riskClass}>{result.risk_category}</span>
            </div>
            <p className="status-line">AI status: {result.ai_status || 'analysis complete'}</p>
            <div className="info-block">
              <h4>Warning signs</h4>
              <ul>
                {result.warning_signs && result.warning_signs.length > 0 ? (
                  result.warning_signs.map((item) => <li key={item}>{item}</li>)
                ) : (
                  <li>No obvious scam warning signs were found in the rule-based checks.</li>
                )}
              </ul>
            </div>
            <div className="info-block">
              <h4>Evidence from the message</h4>
              <ul>
                {result.evidence_from_message && result.evidence_from_message.length > 0 ? (
                  result.evidence_from_message.map((item) => <li key={item}>{item}</li>)
                ) : (
                  <li>No strong evidence detected in the message text alone.</li>
                )}
              </ul>
            </div>
            <div className="info-block">
              <h4>Explanation</h4>
              <p>{result.explanation}</p>
            </div>
            <div className="info-block">
              <h4>Recommended actions</h4>
              <ul>
                {result.recommended_actions && result.recommended_actions.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <div className="info-block">
              <h4>Educational tip</h4>
              <p>{result.educational_tip}</p>
            </div>
            <div className="info-block">
              <h4>Limitations</h4>
              <p>{result.limitations}</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function PaymentCheckerPage() {
  const [values, setValues] = useState({ intended_amount: '500', entered_amount: '5000', recipient_name: 'Asha Sharma' });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const updateField = (field, value) => {
    setValues((current) => ({ ...current, [field]: value }));
  };

  const checkPayment = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/check-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intended_amount: values.intended_amount,
          entered_amount: values.entered_amount,
          recipient_name: values.recipient_name
        })
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(Array.isArray(payload.detail) ? payload.detail.map((item) => item.msg).join(', ') : payload.detail || 'Invalid payment details.');
      }
      setResult(payload);
      setError('');
    } catch (err) {
      setError(err.message || 'Unable to verify payment.');
      setResult(null);
    }
  };

  return (
    <section className="panel-page">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Payment Checker</p>
          <h2>Check payment details before confirming</h2>
        </div>
      </div>
      <div className="panel-body payment-checker">
        <label>
          Intended amount
          <input type="text" value={values.intended_amount} onChange={(event) => updateField('intended_amount', event.target.value)} placeholder="₹500" />
        </label>
        <label>
          Entered amount
          <input type="text" value={values.entered_amount} onChange={(event) => updateField('entered_amount', event.target.value)} placeholder="₹5000" />
        </label>
        <label>
          Recipient name
          <input type="text" value={values.recipient_name} onChange={(event) => updateField('recipient_name', event.target.value)} placeholder="Name of recipient" />
        </label>
        <div className="button-row">
          <button type="button" className="primary-btn" onClick={checkPayment}>Check Again</button>
          <button type="button" className="secondary-btn" onClick={() => updateField('entered_amount', values.intended_amount)}>Edit Amount</button>
          <button type="button" className="secondary-btn" onClick={() => setValues((current) => ({ ...current, recipient_name: '' }))}>Review Recipient</button>
        </div>

        {error && <div className="status-box error-box">{error}</div>}

        {result && (
          <div className="result-box payment-result">
            <h3>{result.status}</h3>
            <p>{result.message}</p>
            {result.warnings.length > 0 && (
              <ul>
                {result.warnings.map((warning) => <li key={warning}>{warning}</li>)}
              </ul>
            )}
            <div className="status-line">Safe to continue: {result.is_safe_to_continue ? 'Yes' : 'No'}</div>
          </div>
        )}
      </div>
    </section>
  );
}

function SafetyAssistantPage() {
  const [question, setQuestion] = useState('I received a message asking for an OTP to unlock my account. What should I do?');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const askQuestion = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ask-safety`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(payload.detail || 'Unable to answer the question.');
      }
      setAnswer(payload.answer || '');
      setError('');
    } catch (err) {
      setError(err.message || 'Unable to answer right now.');
    }
  };

  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Voice input is not supported in this browser.');
      return;
    }
    if (!recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuestion(transcript);
      };
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);
      recognitionRef.current = recognition;
    }

    if (!isListening) {
      recognitionRef.current.start();
      setIsListening(true);
      setError('');
    } else {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const speakAnswer = () => {
    if (!answer) return;
    const speech = new SpeechSynthesisUtterance(answer);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(speech);
  };

  return (
    <section className="panel-page">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Safety Assistant</p>
          <h2>Ask a question about a payment concern</h2>
        </div>
      </div>
      <div className="panel-body">
        <label htmlFor="safety-question" className="field-label">Your question</label>
        <textarea id="safety-question" rows="4" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a safe-payment question" />
        <div className="button-row">
          <button type="button" className="primary-btn" onClick={askQuestion}>Ask</button>
          <button type="button" className="secondary-btn" onClick={handleVoiceInput}>{isListening ? 'Stop listening' : 'Use voice input'}</button>
        </div>
        {error && <div className="status-box error-box">{error}</div>}
        {answer && (
          <div className="result-box">
            <h3>Safety guidance</h3>
            <p>{answer}</p>
            <div className="button-row">
              <button type="button" className="secondary-btn" onClick={speakAnswer}>Listen</button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function LearnSafetyPage() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    const loadScenarios = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/learning-scenarios`);
        const payload = await res.json();
        setScenarios(payload);
      } catch (error) {
        console.error(error);
      }
    };
    loadScenarios();
  }, []);

  const current = scenarios[selectedIndex];

  const handleChoice = (choice) => {
    const isCorrect = current.correct_answer === choice;
    setAnswers((prev) => ({ ...prev, [current.id]: isCorrect }));
    if (isCorrect) setScore((prev) => prev + 1);
    if (selectedIndex < scenarios.length - 1) setSelectedIndex((prev) => prev + 1);
  };

  const resetQuiz = () => {
    setSelectedIndex(0);
    setScore(0);
    setAnswers({});
  };

  if (!scenarios.length) {
    return <div className="empty-state">Loading quiz scenarios…</div>;
  }

  const done = Object.keys(answers).length >= scenarios.length;

  return (
    <section className="panel-page">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Learn Safety</p>
          <h2>Safety quiz</h2>
        </div>
        <div className="score-block">Score: {score}/{scenarios.length}</div>
      </div>
      <div className="panel-body quiz-box">
        {!done ? (
          <>
            <p className="quiz-heading">Scenario {selectedIndex + 1} of {scenarios.length}</p>
            <h3>{current.title}</h3>
            <p>{current.scenario}</p>
            <div className="choice-list">
              {current.choices.map((choice) => (
                <button key={choice} type="button" className="choice-btn" onClick={() => handleChoice(choice)}>
                  {choice}
                </button>
              ))}
            </div>
          </>
        ) : (
          <div className="result-box">
            <h3>Quiz complete</h3>
            <p>Your final score is {score} out of {scenarios.length}.</p>
            <div className="quiz-review">
              {scenarios.map((scenario) => (
                <div key={scenario.id} className="review-item">
                  <strong>{scenario.title}</strong>
                  <p>{scenario.explanation}</p>
                </div>
              ))}
            </div>
            <button type="button" className="primary-btn" onClick={resetQuiz}>Try again</button>
          </div>
        )}
      </div>
    </section>
  );
}

export default App;
