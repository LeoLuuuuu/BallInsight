import { Search, Activity, FlaskConical, Timer, Trophy } from 'lucide-react';

export default function SearchHeader({
    query, setQuery, loading, sentiment, setSentiment, abMode, setAbMode,
    onSearch, onGoHome, queryTime,
}) {
    return (
        <header className="sticky top-0 z-50 backdrop-blur-2xl border-b border-emerald-900/20 pt-5 pb-4 px-8 shadow-2xl flex-shrink-0"
                style={{background: 'linear-gradient(180deg, rgba(8,20,12,0.97) 0%, rgba(8,20,12,0.93) 100%)'}}>
            {/* Floodlight glow bar */}
            <div className="absolute top-0 left-0 right-0 h-px"
                 style={{background: 'linear-gradient(90deg, transparent 0%, #f59e0b 20%, #10b981 50%, #f59e0b 80%, transparent 100%)', backgroundSize: '200% 100%', animation: 'header-glow 3s ease-in-out infinite'}} />

            <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
                {/* Logo */}
                <div className="flex items-center space-x-3 cursor-pointer group" onClick={onGoHome}>
                    <div className="relative w-10 h-10 rounded-xl flex items-center justify-center transition-all group-hover:scale-105"
                         style={{background: 'linear-gradient(135deg, #10b981, #059669)', boxShadow: '0 0 20px rgba(16,185,129,0.35)'}}>
                        <Activity size={24} strokeWidth={2.5} color="#fff" />
                        <div className="absolute inset-0 rounded-xl border border-white/20" />
                    </div>
                    <h1 className="text-2xl font-black text-white tracking-wider">
                        BALL<span style={{color: '#f59e0b'}}>INSIGHT</span>
                    </h1>
                    {queryTime != null && (
                        <span className="flex items-center text-[10px] font-mono px-2 py-0.5 rounded-full border animate-score-pulse"
                              style={{color: '#f59e0b', background: 'rgba(245,158,11,0.1)', borderColor: 'rgba(245,158,11,0.25)'}}>
                            <Timer size={10} className="mr-1" style={{color: '#f59e0b'}} />{queryTime}ms
                        </span>
                    )}
                </div>

                {/* Search bar */}
                <form onSubmit={onSearch} className="flex-1 max-w-2xl mx-12">
                    <div className="relative flex items-center rounded-2xl border shadow-inner transition-all duration-300"
                         style={{
                             background: 'rgba(15,30,20,0.9)',
                             borderColor: 'rgba(16,185,129,0.15)',
                         }}
                         onFocus={(e) => {
                             e.currentTarget.style.borderColor = 'rgba(245,158,11,0.5)';
                             e.currentTarget.style.boxShadow = '0 0 16px rgba(245,158,11,0.1)';
                         }}
                         onBlur={(e) => {
                             e.currentTarget.style.borderColor = 'rgba(16,185,129,0.15)';
                             e.currentTarget.style.boxShadow = 'none';
                         }}>
                        <Search className="absolute left-4 w-5 h-5" style={{color: '#10b981'}} />
                        <input type="text" value={query}
                               onChange={(e) => setQuery(e.target.value)}
                               className="w-full pl-12 pr-4 py-3 bg-transparent outline-none text-base text-white placeholder-slate-500" />
                        <button type="submit"
                                className="absolute right-2 px-5 py-1.5 rounded-xl font-bold transition-all text-sm"
                                style={{
                                    background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                                    color: '#0a1a10',
                                }}>
                            {loading ? '...' : 'SEARCH'}
                        </button>
                    </div>
                </form>

                {/* Controls */}
                <div className="flex items-center space-x-4">
                    <div className="flex p-1 rounded-xl border"
                         style={{background: 'rgba(15,30,20,0.9)', borderColor: 'rgba(16,185,129,0.15)'}}>
                        {['all', 'positive', 'negative'].map(t => (
                            <button key={t}
                                    onClick={() => { setSentiment(t); onSearch(); }}
                                    className="text-xs px-4 py-2 rounded-lg transition-all font-bold tracking-wider"
                                    style={sentiment === t ? {
                                        background: 'rgba(16,185,129,0.15)',
                                        color: '#f59e0b',
                                        boxShadow: '0 0 8px rgba(245,158,11,0.15)',
                                    } : {
                                        color: '#64748b',
                                    }}>
                                {t === 'all' ? 'ALL' : t === 'positive' ? 'HYPE' : 'WARN'}
                            </button>
                        ))}
                    </div>
                    <button onClick={() => setAbMode(!abMode)}
                            className="flex items-center px-4 py-2 rounded-xl text-xs font-black tracking-widest transition-all"
                            style={abMode ? {
                                background: 'rgba(245,158,11,0.15)',
                                color: '#f59e0b',
                                border: '1px solid rgba(245,158,11,0.4)',
                                boxShadow: '0 0 15px rgba(245,158,11,0.2)',
                            } : {
                                background: 'rgba(15,30,20,0.8)',
                                border: '1px solid rgba(16,185,129,0.12)',
                                color: '#94a3b8',
                            }}>
                        <FlaskConical size={16} className="mr-2"/> A/B TEST
                    </button>
                </div>
            </div>
        </header>
    );
}
