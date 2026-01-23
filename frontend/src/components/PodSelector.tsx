import React, { useEffect, useState } from 'react';
import { ChevronDown, Server } from 'lucide-react';
import axios from 'axios';

interface PodSelectorProps {
    onSelectionChange: (selectedPods: string[]) => void;
}

export const PodSelector: React.FC<PodSelectorProps> = ({ onSelectionChange }) => {
    const [pods, setPods] = useState<string[]>([]);
    const [pod1, setPod1] = useState<string>('');
    const [pod2, setPod2] = useState<string>('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPods = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/v1/metrics/pods');
                setPods(res.data.pods || []);
            } catch (err) {
                console.error("Failed to fetch pods", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPods();
    }, []);

    useEffect(() => {
        const selection = [pod1, pod2].filter(p => p !== '');
        onSelectionChange(selection);
    }, [pod1, pod2, onSelectionChange]);

    if (loading) return <div className="text-gray-500 text-xs p-2">Loading pods...</div>;

    return (
        <div className="flex flex-col gap-2 p-4 bg-dark-surface border-b border-gray-700">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-300">
                <Server size={14} />
                <span>Compare Pods</span>
            </div>
            <div className="flex gap-4">
                <div className="relative w-48">
                    <select
                        className="w-full bg-gray-800 text-white text-sm border border-gray-600 rounded px-2 py-1 appearance-none focus:ring-2 focus:ring-primary outline-none"
                        value={pod1}
                        onChange={(e) => setPod1(e.target.value)}
                    >
                        <option value="">Select Pod A...</option>
                        {pods.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <ChevronDown size={14} className="absolute right-2 top-2 text-gray-400 pointer-events-none" />
                </div>

                <div className="relative w-48">
                    <select
                        className="w-full bg-gray-800 text-white text-sm border border-gray-600 rounded px-2 py-1 appearance-none focus:ring-2 focus:ring-primary outline-none"
                        value={pod2}
                        onChange={(e) => setPod2(e.target.value)}
                    >
                        <option value="">Select Pod B...</option>
                        {pods.filter(p => p !== pod1).map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <ChevronDown size={14} className="absolute right-2 top-2 text-gray-400 pointer-events-none" />
                </div>
            </div>
        </div>
    );
};
