import React, { useState, useRef, useEffect } from 'react';
import { Send, Activity } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { sendMessageStream, ChatMessage } from '../services/api';

export const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg: ChatMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Create a placeholder for the assistant
            let fullResponse = '';
            setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

            await sendMessageStream(userMsg.content, messages, (chunk) => {
                fullResponse += chunk;
                setMessages(prev => {
                    const newHistory = [...prev];
                    const lastMsg = newHistory[newHistory.length - 1];
                    if (lastMsg.role === 'assistant') {
                        lastMsg.content = fullResponse;
                    }
                    return newHistory;
                });
            });
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: '**Error**: Failed to connect to backend.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-dark text-gray-100 font-sans">
            {/* Header */}
            <header className="flex items-center px-6 py-4 border-b border-gray-700 bg-dark-surface">
                <Activity className="text-primary mr-3" />
                <h1 className="text-xl font-bold tracking-tight">AI Observability Assistant</h1>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500 opacity-50">
                        <Activity size={64} className="mb-4" />
                        <p className="text-lg">Ask about your infrastructure metrics...</p>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <MessageBubble key={idx} role={msg.role} content={msg.content} />
                ))}

                {isLoading && (
                    <div className="flex justify-start w-full mb-6">
                        <div className="flex max-w-[80%] md:max-w-[70%] flex-row">
                            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-green-600 flex items-center justify-center mx-2">
                                <Bot size={16} className="text-white animate-pulse" />
                            </div>
                            <div className="p-4 bg-dark-surface border border-gray-700 rounded-2xl rounded-tl-sm text-sm text-gray-400">
                                Thinking...
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-dark-surface border-t border-gray-700">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder="Ask a question (e.g., 'Compare CPU usage of pod-a vs pod-b')"
                        className="w-full bg-gray-800 text-white rounded-full pl-6 pr-12 py-4 focus:outline-none focus:ring-2 focus:ring-primary shadow-lg border border-gray-700 placeholder-gray-500"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 bg-primary rounded-full hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={18} className="text-white" />
                    </button>
                </form>
            </div>
        </div>
    );
};

// Simple visual components for import fix
const Bot = ({ size, className }: { size: number, className?: string }) => (
    <svg width={size} height={size} className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z" /><path d="m5 7 1.5 1.5" /><path d="m19 7-1.5 1.5" /><path d="M7 10h10a3 3 0 0 1 3 3v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a3 3 0 0 1 3-3Z" /><path d="M12 15h.01" /></svg>
);
