import { Clock, Zap, AlertTriangle } from 'lucide-react';

const STOCK_IMAGES = [
    "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=500&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1518605368461-1ee7e57cdde6?w=500&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=500&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=500&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1614632537190-23e4146777db?w=500&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=500&q=80&auto=format&fit=crop",
];

function getImage(id) {
    if (!id) return STOCK_IMAGES[0];
    let hash = 0;
    const s = id.toString();
    for (let i = 0; i < s.length; i++) {
        hash = ((hash << 5) - hash + s.charCodeAt(i)) | 0;
    }
    return STOCK_IMAGES[Math.abs(hash) % STOCK_IMAGES.length];
}

export default function NewsCard({ item, onClick }) {
    const isPositive = item.sentiment_score >= 60;
    const isNegative = item.sentiment_score <= 40;
    const SentimentIcon = isPositive ? Zap : isNegative ? AlertTriangle : Clock;

    return (
        <article onClick={() => onClick(item)}
                 className="cursor-pointer group relative backdrop-blur-sm rounded-2xl border transition-all duration-300 overflow-hidden flex gap-5 p-5 gold-shimmer"
                 style={{
                     background: 'linear-gradient(135deg, rgba(15,30,20,0.6), rgba(10,20,14,0.7))',
                     borderColor: 'rgba(16,185,129,0.1)',
                 }}
                 onMouseEnter={e => {
                     e.currentTarget.style.borderColor = 'rgba(245,158,11,0.3)';
                     e.currentTarget.style.boxShadow = '0 8px 30px rgba(245,158,11,0.06)';
                     e.currentTarget.style.transform = 'translateY(-2px)';
                 }}
                 onMouseLeave={e => {
                     e.currentTarget.style.borderColor = 'rgba(16,185,129,0.1)';
                     e.currentTarget.style.boxShadow = 'none';
                     e.currentTarget.style.transform = 'none';
                 }}>

            {/* Gold stripe accent on hover */}
            <div className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-all duration-500"
                 style={{background: 'linear-gradient(90deg, transparent, #f59e0b, transparent)'}} />

            {/* Image with grass-tinted overlay */}
            <div className="w-28 h-28 rounded-xl flex-shrink-0 relative overflow-hidden group-hover:border transition-colors shadow-lg"
                 style={{background: '#0a1a10', borderColor: 'rgba(16,185,129,0.15)'}}>
                <img src={getImage(item.news_id)} alt=""
                     className="w-full h-full object-cover opacity-75 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500" />
                <div className="absolute inset-0" style={{background: 'linear-gradient(to top, rgba(10,25,15,0.8), transparent 50%, transparent)'}} />
                {/* Jersey number badge - gold */}
                <div className="absolute bottom-1.5 right-1.5 w-7 h-7 rounded flex items-center justify-center border animate-score-pulse"
                     style={{
                         background: 'linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.08))',
                         borderColor: 'rgba(245,158,11,0.3)',
                     }}>
                    <span className="text-[9px] font-black" style={{color: '#f59e0b'}}>{item.final_score?.toFixed(0)}</span>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 flex flex-col justify-between min-w-0">
                <div>
                    <h2 className="text-sm font-bold mb-1.5 transition-colors leading-snug line-clamp-1"
                        style={{color: '#e2e8f0'}}
                        dangerouslySetInnerHTML={{ __html: item.title }}
                        onMouseEnter={e => e.target.style.color = '#f59e0b'}
                        onMouseLeave={e => e.target.style.color = '#e2e8f0'} />
                    <p className="text-xs leading-relaxed line-clamp-2" style={{color: '#94a3b8'}}
                       dangerouslySetInnerHTML={{ __html: item.snippet }} />
                </div>

                <div className="flex items-center gap-3 mt-3 text-[10px] font-semibold">
                    <span className="flex items-center gap-1" style={{color: '#64748b'}}>
                        <Clock size={10} />
                        {item.publish_time?.slice(0, 10) || '未知'}
                    </span>
                    <span className="flex items-center gap-1 px-2 py-0.5 rounded-md font-bold" style={
                        isPositive
                            ? {color: '#10b981', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)'}
                            : isNegative
                                ? {color: '#ef4444', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)'}
                                : {color: '#94a3b8', background: 'rgba(100,116,139,0.1)', border: '1px solid rgba(100,116,139,0.15)'}
                    }>
                        <SentimentIcon size={10} />
                        {item.sentiment_score}
                    </span>
                    <span className="ml-auto text-[10px] opacity-0 group-hover:opacity-100 transition-opacity font-bold tracking-wide"
                          style={{color: '#f59e0b'}}>
                        阅读全文 →
                    </span>
                </div>
            </div>
        </article>
    );
}
