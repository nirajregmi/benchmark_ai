import React from 'react';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content }) => {
    const isUser = role === 'user';

    return (
        <div className={clsx(
            "flex w-full mb-6",
            isUser ? "justify-end" : "justify-start"
        )}>
            <div className={clsx(
                "flex max-w-[80%] md:max-w-[70%]",
                isUser ? "flex-row-reverse" : "flex-row"
            )}>
                {/* Avatar */}
                <div className={clsx(
                    "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center mx-2",
                    isUser ? "bg-blue-600" : "bg-green-600"
                )}>
                    {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                </div>

                {/* Bubble */}
                <div className={clsx(
                    "p-4 rounded-2xl text-sm leading-relaxed shadow-sm",
                    isUser
                        ? "bg-blue-600 text-white rounded-tr-sm"
                        : "bg-dark-surface border border-gray-700 text-gray-100 rounded-tl-sm"
                )}>
                    <div className="prose prose-invert max-w-none">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                </div>
            </div>
        </div>
    );
};
