import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { chatApi, ChatMessage } from '../api/client';

export default function Chat() {
  const { projectId } = useParams<{ projectId: string }>();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!message.trim() || !projectId) return;

    const userMessage = message;
    setMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const history = messages.map(m => ({
        role: m.role,
        content: m.content,
      }));

      const response = await chatApi.sendMessage(parseInt(projectId), userMessage, history);
      setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '抱歉，发生了错误。请稍后重试。' },
      ]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-tech-blue/20">
        <h2 className="font-orbitron text-2xl font-bold text-tech-blue neon-text">
          AI 问答
        </h2>
        <p className="text-sm text-gray-400 mt-1">基于代码知识图谱的智能问答助手</p>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="glass-card p-8 text-center max-w-2xl mx-auto">
            <Bot className="w-16 h-16 text-tech-blue mx-auto mb-4 neon-text" />
            <h3 className="text-xl text-gray-300 mb-2">开始对话</h3>
            <p className="text-gray-500 mb-4">
              询问关于代码库的任何问题，我会基于代码结构信息为您解答
            </p>
            <div className="text-left text-sm text-gray-400 space-y-2">
              <p>你可以问：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>"这个项目有哪些主要类？"</li>
                <li>"函数 X 在哪里定义？"</li>
                <li>"类型 A 和类型 B 有什么关系？"</li>
                <li>"解释某个模块的功能"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-tech-blue/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-tech-blue" />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-tech-blue to-quantum-purple text-white'
                    : 'glass-card text-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-neon-green/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-neon-green" />
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-tech-blue/20 flex items-center justify-center">
              <Bot className="w-5 h-5 text-tech-blue" />
            </div>
            <div className="glass-card p-4">
              <div className="flex items-center gap-2 text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>正在思考...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-tech-blue/20">
        <div className="glass-card p-4">
          <div className="flex gap-3">
            <textarea
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题..."
              className="flex-1 bg-space-dark border border-tech-blue/30 rounded-lg px-4 py-3 resize-none focus:outline-none focus:border-tech-blue focus:shadow-[0_0_15px_rgba(0,212,255,0.5)] transition-all"
              rows={2}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!message.trim() || loading}
              className="glow-button flex items-center gap-2 self-end"
            >
              <Send className="w-4 h-4" />
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
