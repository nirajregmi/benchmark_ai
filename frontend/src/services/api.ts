

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export const sendMessageStream = async (
    message: string,
    history: ChatMessage[],
    selectedPods: string[],
    onChunk: (chunk: string) => void
) => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, history, selected_pods: selectedPods }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                // Clean up SSE prefix if present (simple implementation)
                const lines = chunk.split('\n\n');
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        onChunk(line.slice(6));
                    } else if (line.trim() !== '') {
                        // Direct text fallback
                        onChunk(line);
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};

export const downloadReport = async (selectedPods: string[]) => {
    try {
        const response = await fetch(`${API_BASE_URL}/report/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: 'Generate Report', selected_pods: selectedPods }),
        });

        if (!response.ok) {
            throw new Error('Report generation failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `benchmark_report_${new Date().toISOString().slice(0, 10)}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error downloading report:', error);
        throw error;
    }
};
