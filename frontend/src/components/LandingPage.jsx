import {
    Search, Activity, Clock, Zap, Database, Terminal, Hexagon,
    Compass, Radio, Network, Newspaper, Flame, Trophy,
} from 'lucide-react';

const STATS = [
    { icon: Database, color: 'emerald', value: '5,248', label: '全息赛事档案库', sub: 'BM25 倒排索引就绪' },
    { icon: Hexagon, color: 'amber', value: '11,484', label: '球员六维雷达网', sub: '战术节点解析完成' },
    { icon: Zap, color: 'emerald', value: '混合动力重排', label: '战术时效 + 舆情偏好', sub: '双轨制评分在线验证' },
];

const colorMap = {
    emerald: { bg: 'rgba(16,185,129,0.12)', text: '#10b981', border: 'rgba(16,185,129,0.25)' },
    amber:   { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)' },
};

export default function LandingPage({
    query, setQuery, loading, onSearch, onQuickSearch, trendingTags, landingNews, onSelectArticle,
}) {
    return (
        <div className="min-h-screen flex flex-col relative overflow-hidden font-sans"
             style={{background: 'linear-gradient(180deg, #0a1a10 0%, #0d1f14 30%, #07100a 100%)'}}>
            {/* Background layers */}
            <div className="absolute inset-0 z-0">
                {/* Unsplash football bg */}
                <img src="https://images.unsplash.com/photo-1508344928928-7151b67de5b3?q=80&w=2000&auto=format&fit=crop"
                     alt="" className="w-full h-full object-cover opacity-[0.06] mix-blend-luminosity scale-105"
                     style={{filter: 'saturate(0.3)'}} />
                {/* Pitch grid */}
                <div className="absolute inset-0 pitch-grid opacity-25"
                     style={{transform: 'perspective(800px) rotateX(50deg) scale(2.2)', transformOrigin: 'bottom center'}} />
                {/* Pitch stripes */}
                <div className="absolute inset-0 pitch-stripe opacity-20" />
                {/* Center circle */}
                <div className="absolute top-[55%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-44 h-44 rounded-full border opacity-0 animate-[circle-glow_4s_ease-in-out_infinite]"
                     style={{borderColor: 'rgba(245,158,11,0.12)'}} />
                {/* Halfway line */}
                <div className="absolute top-[55%] left-0 right-0 h-px opacity-20"
                     style={{background: 'linear-gradient(90deg, transparent, rgba(245,158,11,0.25), transparent)'}} />
                {/* Ambient light */}
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] blur-[120px] rounded-full pointer-events-none"
                     style={{background: 'rgba(16,185,129,0.07)'}} />
                <div className="absolute bottom-0 left-0 w-full h-[500px] pointer-events-none"
                     style={{background: 'linear-gradient(to top, rgba(16,185,129,0.06), transparent)'}} />
            </div>

            {/* Header */}
            <header className="relative z-10 w-full p-8 flex justify-between items-center">
                <div className="flex items-center space-x-3 opacity-90 hover:opacity-100 transition-opacity cursor-pointer">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center relative overflow-hidden shadow-lg"
                         style={{background: 'linear-gradient(135deg, #10b981, #059669)', boxShadow: '0 0 18px rgba(16,185,129,0.4)'}}>
                        <Activity size={19} strokeWidth={3} color="#fff" className="relative z-10" />
                        <div className="absolute inset-0 bg-white/20 animate-ping" style={{animationDuration: '2s'}} />
                    </div>
                    <span className="text-xl font-black text-white tracking-widest">
                        BALL<span style={{color: '#f59e0b'}}>INSIGHT</span>
                    </span>
                </div>
                <div className="flex items-center space-x-6">
                    <span className="flex items-center text-xs font-mono px-3 py-1.5 rounded-full border"
                          style={{color: '#10b981', background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.2)'}}>
                        <span className="w-2 h-2 rounded-full mr-2 animate-pulse" style={{background: '#10b981'}} />
                        SYSTEM ONLINE
                    </span>
                    <span className="text-sm font-bold tracking-widest uppercase flex items-center" style={{color: '#94a3b8'}}>
                        <Compass size={16} className="mr-2" /> 实验任务大作业
                    </span>
                </div>
            </header>

            {/* Hero */}
            <main className="flex-1 relative z-10 flex flex-col items-center justify-center px-4 -mt-6">
                <div className="text-center mb-10 relative">
                    <div className="absolute -inset-6 blur-2xl rounded-full opacity-40"
                         style={{background: 'rgba(16,185,129,0.08)'}} />
                    {/* Trophy icon */}
                    <div className="flex justify-center mb-4">
                        <Trophy size={36} style={{color: '#f59e0b', filter: 'drop-shadow(0 0 8px rgba(245,158,11,0.3))'}} />
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-4 drop-shadow-2xl"
                        style={{
                            background: 'linear-gradient(135deg, #10b981 0%, #f59e0b 40%, #fbbf24 60%, #ffffff 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            backgroundClip: 'text',
                        }}>
                        感知赛场脉搏
                    </h1>
                    <p className="text-lg md:text-xl font-medium tracking-wide flex items-center justify-center" style={{color: '#94a3b8'}}>
                        <Network className="w-5 h-5 mr-2" style={{color: '#10b981'}} />
                        融合知识图谱与多模态的智能足球检索系统
                    </p>
                </div>

                {/* Search bar */}
                <form onSubmit={onSearch} className="w-full max-w-3xl relative group z-20">
                    <div className="absolute -inset-1 rounded-[2rem] blur opacity-25 group-hover:opacity-50 transition duration-500"
                         style={{background: 'linear-gradient(90deg, #10b981, #f59e0b, #10b981)', backgroundSize: '200% 100%', animation: 'header-glow 3s ease-in-out infinite'}} />
                    <div className="relative flex items-center backdrop-blur-xl rounded-[2rem] border p-2"
                         style={{background: 'rgba(10,24,16,0.95)', borderColor: 'rgba(16,185,129,0.15)'}}>
                        <Search className="absolute left-6 w-7 h-7" style={{color: '#10b981'}} />
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="探索赛事全息切片、球员图谱或最新战况..."
                            className="w-full pl-16 pr-6 py-5 bg-transparent outline-none text-xl text-white placeholder-slate-500 font-medium"
                        />
                        <button type="submit"
                                className="px-8 py-4 rounded-2xl font-black text-lg transition-all flex items-center group-hover:scale-105"
                                style={{
                                    background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                                    color: '#0a1a10',
                                    boxShadow: '0 0 20px rgba(245,158,11,0.25)',
                                }}>
                            {loading ? <Clock className="animate-spin w-6 h-6" /> : '启动检索'}
                        </button>
                    </div>
                </form>

                {/* Trending tags */}
                <div className="mt-8 w-full max-w-3xl z-20">
                    <div className="flex items-center justify-center space-x-2 mb-4 text-sm font-bold tracking-widest uppercase" style={{color: '#94a3b8'}}>
                        <Flame size={16} style={{color: '#f59e0b'}} /> <span>Trending Now</span>
                    </div>
                    <div className="flex flex-wrap justify-center gap-3">
                        {trendingTags.map(tag => (
                            <button key={tag} onClick={() => onQuickSearch(tag)}
                                    className="px-5 py-2 rounded-full border backdrop-blur-md transition-all font-medium"
                                    style={{
                                        background: 'rgba(15,30,20,0.7)',
                                        borderColor: 'rgba(16,185,129,0.15)',
                                        color: '#cbd5e1',
                                    }}
                                    onMouseEnter={e => {
                                        e.target.style.background = 'rgba(245,158,11,0.12)';
                                        e.target.style.color = '#f59e0b';
                                        e.target.style.borderColor = 'rgba(245,158,11,0.35)';
                                    }}
                                    onMouseLeave={e => {
                                        e.target.style.background = 'rgba(15,30,20,0.7)';
                                        e.target.style.color = '#cbd5e1';
                                        e.target.style.borderColor = 'rgba(16,185,129,0.15)';
                                    }}>
                                {tag}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stats cards */}
                <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl z-10">
                    {STATS.map(({ icon: Icon, color, value, label, sub }) => (
                        <div key={label}
                             className="backdrop-blur-md border rounded-3xl p-6 flex items-start space-x-4 transition-all group gold-shimmer relative overflow-hidden"
                             style={{background: 'rgba(15,30,20,0.65)', borderColor: 'rgba(16,185,129,0.12)'}}
                             onMouseEnter={e => {
                                 e.currentTarget.style.background = 'rgba(20,40,25,0.75)';
                                 e.currentTarget.style.borderColor = 'rgba(245,158,11,0.25)';
                             }}
                             onMouseLeave={e => {
                                 e.currentTarget.style.background = 'rgba(15,30,20,0.65)';
                                 e.currentTarget.style.borderColor = 'rgba(16,185,129,0.12)';
                             }}>
                            <div className="p-3 rounded-2xl transition-all group-hover:scale-110" style={{background: colorMap[color].bg}}>
                                <Icon size={28} style={{color: colorMap[color].text}} />
                            </div>
                            <div>
                                <h3 className="text-3xl font-black tracking-tight" style={{color: '#e2e8f0'}}>{value}</h3>
                                <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{color: '#94a3b8'}}>{label}</p>
                                <p className="text-[10px] font-mono mt-2 flex items-center" style={{color: '#64748b'}}>
                                    <Terminal size={10} className="mr-1"/> {sub}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Landing news - scoreboard style */}
                <div className="mt-12 w-full max-w-6xl z-10 pb-16">
                    <div className="flex items-center justify-between mb-6 pb-4" style={{borderBottom: '1px solid rgba(16,185,129,0.08)'}}>
                        <h3 className="text-xl font-black text-white tracking-widest uppercase flex items-center">
                            <div className="relative mr-3">
                                <Radio size={20} style={{color: '#f59e0b'}} />
                                <span className="absolute top-0 right-0 w-2 h-2 rounded-full animate-[live-dot_1.5s_ease-in-out_infinite]" style={{background: '#f59e0b'}} />
                            </div>
                            24H 实时足坛简报
                            <span className="text-[10px] px-2 py-1 rounded ml-3 border font-mono"
                                  style={{color: '#f59e0b', background: 'rgba(245,158,11,0.08)', borderColor: 'rgba(245,158,11,0.2)'}}>LIVE UPLINK</span>
                        </h3>
                        <button onClick={() => onQuickSearch('')}
                                className="text-xs font-bold tracking-widest uppercase flex items-center transition-colors group"
                                style={{color: '#f59e0b'}}>
                            查阅全库战况 <Compass size={14} className="ml-1 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {landingNews.length > 0 ? landingNews.map((item, idx) => (
                            <div key={`landing-${idx}`} onClick={() => onSelectArticle(item)}
                                 className="cursor-pointer backdrop-blur-sm rounded-2xl border p-5 group transition-all flex flex-col justify-between min-h-[160px] gold-shimmer relative overflow-hidden"
                                 style={{
                                     background: 'rgba(15,30,20,0.55)',
                                     borderColor: 'rgba(16,185,129,0.1)',
                                     animation: `card-rise 0.4s ease-out ${idx * 0.1}s both`,
                                 }}
                                 onMouseEnter={e => {
                                     e.currentTarget.style.borderColor = 'rgba(245,158,11,0.3)';
                                     e.currentTarget.style.transform = 'translateY(-4px)';
                                     e.currentTarget.style.boxShadow = '0 12px 40px rgba(245,158,11,0.08)';
                                 }}
                                 onMouseLeave={e => {
                                     e.currentTarget.style.borderColor = 'rgba(16,185,129,0.1)';
                                     e.currentTarget.style.transform = 'translateY(0)';
                                     e.currentTarget.style.boxShadow = 'none';
                                 }}>
                                <div>
                                    <div className="flex items-center space-x-2 mb-3">
                                        <span className="w-2 h-2 rounded-full animate-pulse" style={{background: '#10b981'}} />
                                        <span className="text-[10px] font-mono tracking-wider" style={{color: '#64748b'}}>
                                            {item.publish_time.split(' ')[0]}
                                        </span>
                                    </div>
                                    <h4 className="text-sm font-bold line-clamp-2 leading-relaxed transition-colors"
                                        style={{color: '#e2e8f0'}}
                                        dangerouslySetInnerHTML={{ __html: item.title }}
                                        onMouseEnter={e => e.target.style.color = '#f59e0b'}
                                        onMouseLeave={e => e.target.style.color = '#e2e8f0'} />
                                </div>
                                <div className="mt-4 flex items-center justify-between">
                                    <span className="text-[10px] px-2 py-1 rounded font-bold" style={
                                        item.sentiment_score > 60
                                            ? {background: 'rgba(16,185,129,0.12)', color: '#10b981'}
                                            : item.sentiment_score < 40
                                                ? {background: 'rgba(239,68,68,0.12)', color: '#ef4444'}
                                                : {background: 'rgba(100,116,139,0.12)', color: '#94a3b8'}
                                    }>
                                        舆情侦测: {item.sentiment_score}
                                    </span>
                                    <Newspaper size={14} style={{color: '#64748b'}} />
                                </div>
                            </div>
                        )) : [1,2,3].map(i => (
                            <div key={i} className="rounded-2xl border p-5 min-h-[160px] animate-pulse"
                                 style={{background: 'rgba(15,30,20,0.3)', borderColor: 'rgba(16,185,129,0.06)'}}>
                                <div className="space-y-3">
                                    <div className="h-2 w-1/4 rounded" style={{background: 'rgba(16,185,129,0.1)'}} />
                                    <div className="h-4 w-full rounded" style={{background: 'rgba(16,185,129,0.08)'}} />
                                    <div className="h-4 w-3/4 rounded" style={{background: 'rgba(16,185,129,0.08)'}} />
                                </div>
                                <div className="h-6 w-1/3 rounded mt-4" style={{background: 'rgba(16,185,129,0.08)'}} />
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}
