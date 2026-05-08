import { X, FileText, Clock } from 'lucide-react';

export default function ArticleModal({ article, onClose }) {
    if (!article) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8" style={{animation: 'card-rise 0.3s ease-out'}}>
            <div className="absolute inset-0 backdrop-blur-md" onClick={onClose}
                 style={{background: 'rgba(5,15,8,0.85)'}} />
            <div className="relative w-full max-w-4xl max-h-[85vh] border rounded-3xl flex flex-col overflow-hidden shadow-2xl"
                 style={{
                     background: 'linear-gradient(180deg, #0d1f14, #0a1a10)',
                     borderColor: 'rgba(245,158,11,0.2)',
                     boxShadow: '0 0 50px rgba(245,158,11,0.08)',
                 }}>
                {/* Title bar */}
                <div className="flex items-center justify-between p-6 border-b"
                     style={{background: 'rgba(15,30,20,0.5)', borderColor: 'rgba(16,185,129,0.1)'}}>
                    <div className="flex items-center space-x-3" style={{color: '#f59e0b'}}>
                        <FileText size={24} />
                        <h2 className="text-lg font-bold tracking-wide line-clamp-1" style={{color: '#e2e8f0'}}
                            dangerouslySetInnerHTML={{ __html: article.title }} />
                    </div>
                    <button onClick={onClose}
                            className="p-2 rounded-full transition-colors"
                            style={{background: 'rgba(15,30,20,0.8)', color: '#94a3b8'}}
                            onMouseEnter={e => { e.target.style.background = '#1e3a28'; e.target.style.color = '#fff'; }}
                            onMouseLeave={e => { e.target.style.background = 'rgba(15,30,20,0.8)'; e.target.style.color = '#94a3b8'; }}>
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-8 overflow-y-auto flex-1 custom-scrollbar space-y-6">
                    <div className="flex items-center space-x-4 text-xs font-bold uppercase tracking-widest mb-6 pb-6 border-b border-dashed"
                         style={{color: '#64748b', borderColor: 'rgba(16,185,129,0.1)'}}>
                        <span className="flex items-center" style={{color: '#10b981'}}>
                            <Clock size={14} className="mr-1"/> {article.publish_time}
                        </span>
                        <span style={{color: article.sentiment_score > 60 ? '#10b981' : article.sentiment_score < 40 ? '#ef4444' : '#94a3b8'}}>
                            情感打分: {article.sentiment_score}
                        </span>
                        <span style={{color: '#f59e0b'}}>检索权重: {article.final_score}</span>
                    </div>
                    <div className="max-w-none">
                        {article.full_content ? (
                            <p className="leading-loose text-base whitespace-pre-wrap" style={{color: '#cbd5e1'}}>
                                {article.full_content}
                            </p>
                        ) : (
                            <p className="leading-loose text-base" style={{color: '#cbd5e1'}}
                               dangerouslySetInnerHTML={{ __html: article.snippet }} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
