import React, { useState, useEffect } from 'react';
import { Zap, TrendingUp, Radio, Search, Network, User } from 'lucide-react';

import LandingPage from './components/LandingPage';
import SearchHeader from './components/SearchHeader';
import NewsCard from './components/NewsCard';
import ArticleModal from './components/ArticleModal';
import HoloSlice from './components/HoloSlice';
import EntityPanel from './components/EntityPanel';
import ABTestPanel from './components/ABTestPanel';

const API_BASE = 'http://127.0.0.1:8000/api';

const HOLO_DATABASE = [
    {
        keywords: ["c罗", "cristiano ronaldo", "总裁", "倒钩", "倒挂金钩"],
        title: "时空切片：克里斯蒂亚诺·罗纳尔多 史诗级倒钩",
        date: "2018-04-03",
        tactical_data: ["击球高度: 2.38m", "最高时速: 32km/h", "xG (预期进球): 0.02"],
        media_url: "/assets/gifs/CR7.gif",
    },
    {
        keywords: ["梅西", "lionel messi", "老板", "连过五人", "一条龙"],
        title: "时空切片：利昂内尔·梅西 世纪重演",
        date: "2007-04-18",
        tactical_data: ["带球距离: 55m", "过人次数: 5", "突进耗时: 12.1s"],
        media_url: "/assets/gifs/Messi.gif",
    },
    {
        keywords: ["哈兰德", "erling haaland", "魔人", "飞踢"],
        title: "时空切片：埃尔林·哈兰德 暴力美学",
        date: "2022-09-14",
        tactical_data: ["腾空高度: 2.12m", "触球部位: 左脚外脚背", "爆发力评估: S级"],
        media_url: "/assets/gifs/erling-haaland.gif",
    },
];

const TRENDING_TAGS = ['梅西', '皇家马德里', '亚马尔', '欧冠战报', '哈兰德', '曼城', 'C罗倒挂金钩'];

export default function App() {
    const [hasSearched, setHasSearched] = useState(false);
    const [query, setQuery] = useState('');
    const [sentiment, setSentiment] = useState('all');
    const [loading, setLoading] = useState(false);
    const [isFullView, setIsFullView] = useState(false);
    const [abMode, setAbMode] = useState(false);

    const [results, setResults] = useState([]);
    const [baselineResults, setBaselineResults] = useState([]);
    const [tfidfResults, setTfidfResults] = useState([]);
    const [irMetrics, setIrMetrics] = useState(null);
    const [mappedQuery, setMappedQuery] = useState('');
    const [entityType, setEntityType] = useState(null);
    const [entityData, setEntityData] = useState(null);
    const [entityNotFound, setEntityNotFound] = useState(false);

    const [aiSummary, setAiSummary] = useState('');
    const [aiSummaryLoading, setAiSummaryLoading] = useState(false);
    const [aiBio, setAiBio] = useState('');
    const [aiBioLoading, setAiBioLoading] = useState(false);

    const [queryTime, setQueryTime] = useState(null);
    const [totalResults, setTotalResults] = useState(0);
    const [searchError, setSearchError] = useState('');
    const [page, setPage] = useState(0);
    const pageSize = 10;

    const [spellSuggestions, setSpellSuggestions] = useState([]);

    const [holoData, setHoloData] = useState(null);
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [landingNews, setLandingNews] = useState([]);

    // Landing page news
    useEffect(() => {
        fetch(`${API_BASE}/search?q=战报&sentiment=all`)
            .then(r => r.json())
            .then(d => { if (d.status === 'success') setLandingNews(d.results.slice(0, 3)); })
            .catch(() => {});
    }, []);

    // ── Search ────────────────────────────────────────────────

    const executeSearch = async (keyword, currentSentiment, loadMore = false) => {
        if (!loadMore) {
            setLoading(true);
            setPage(0);
            setSearchError('');
        }
        setHasSearched(true);
        setEntityData(null); setEntityType(null); setEntityNotFound(false);
        setAiSummary(''); setAiBio(''); setHoloData(null); setSelectedArticle(null);

        const isAll = keyword.trim() === '';
        setIsFullView(isAll);

        if (!isAll && !loadMore) {
            const matched = HOLO_DATABASE.find(h =>
                h.keywords.some(k => keyword.toLowerCase().includes(k)));
            if (matched) setHoloData(matched);
        }

        try {
            const offset = loadMore ? (page + 1) * pageSize : 0;
            const resp = await fetch(
                `${API_BASE}/search/compare?q=${encodeURIComponent(keyword)}&sentiment=${currentSentiment}&offset=${offset}&limit=${pageSize}`);
            const data = await resp.json();
            if (data.status !== 'success') {
                setSearchError('检索服务异常，请稍后重试');
                return;
            }

            setQueryTime(data.query_time_ms || null);
            setTotalResults(data.total || 0);

            if (loadMore) {
                setResults(prev => [...prev, ...(data.results || [])]);
                setBaselineResults(prev => [...prev, ...(data.baseline_results || [])]);
                setTfidfResults(prev => [...prev, ...(data.tfidf_results || [])]);
                setPage(prev => prev + 1);
            } else {
                setResults(data.results || []);
                setBaselineResults(data.baseline_results || []);
                setTfidfResults(data.tfidf_results || []);
                setIrMetrics(data.metrics || null);
            }

            const entity = data.query.mapped;
            setMappedQuery(entity && entity !== keyword ? entity : '');

            if (!isAll && !loadMore) {
                if (data.results.length > 0 && !abMode) {
                    fetchAiSummary(entity || keyword, data.results);
                }
                if (data.results.length === 0) {
                    fetchSpellSuggestions(keyword);
                } else {
                    setSpellSuggestions([]);
                }
                fetchEntityDetails(entity || keyword, data.results.length === 0);
            }
        } catch (e) {
            console.error("检索失败:", e);
            setSearchError('网络连接失败，请检查后端服务是否启动');
        } finally {
            if (!loadMore) setLoading(false);
        }
    };

    const handleSearch = (e) => {
        if (e) e.preventDefault();
        executeSearch(query, sentiment);
    };
    const handleQuickSearch = (tag) => { setQuery(tag); executeSearch(tag, sentiment); };
    const goHome = () => { setHasSearched(false); setAbMode(false); setIsFullView(false); };

    // ── AI ────────────────────────────────────────────────────

    const fetchAiSummary = async (keyword, searchResults) => {
        setAiSummaryLoading(true);
        try {
            const res = await fetch(`${API_BASE}/ai/summary`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword, results: searchResults }),
            });
            setAiSummary((await res.json()).ai_summary);
        } catch { setAiSummary('AI 服务排队中，请稍后再试。'); }
        finally { setAiSummaryLoading(false); }
    };

    const fetchEntityDetails = async (entityName, needsBio) => {
        try {
            const res = await fetch(`${API_BASE}/entity/${encodeURIComponent(entityName)}`);
            const data = await res.json();
            if (data.status === 'success') {
                setEntityType(data.type); setEntityData(data.data); setEntityNotFound(false);
                if (needsBio) fetchAiBio(data.data);
            } else { setEntityNotFound(true); }
        } catch { setEntityNotFound(true); }
    };

    const fetchAiBio = async (payload) => {
        setAiBioLoading(true);
        try {
            const res = await fetch(`${API_BASE}/ai/bio`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_data: payload }),
            });
            setAiBio((await res.json()).ai_bio);
        } catch { setAiBio('暂无详细 AI 传记介绍。'); }
        finally { setAiBioLoading(false); }
    };

    const fetchSpellSuggestions = async (keyword) => {
        try {
            const res = await fetch(`${API_BASE}/spell/check?q=${encodeURIComponent(keyword)}`);
            const data = await res.json();
            setSpellSuggestions(data.suggestions || []);
        } catch { setSpellSuggestions([]); }
    };

    const onGraphClick = (params) => {
        if (params.dataType === 'node' && params.name) handleQuickSearch(params.name);
    };

    // ── Render ────────────────────────────────────────────────

    if (!hasSearched) {
        return (
            <LandingPage
                query={query} setQuery={setQuery} loading={loading}
                onSearch={handleSearch} onQuickSearch={handleQuickSearch}
                trendingTags={TRENDING_TAGS} landingNews={landingNews}
                onSelectArticle={setSelectedArticle}
            />
        );
    }

    return (
        <div className="min-h-screen text-slate-200 font-sans relative overflow-hidden flex flex-col" style={{background: 'linear-gradient(180deg, #0a1a10 0%, #0d1f14 30%, #0b180e 60%, #09120b 100%)'}}>
            {selectedArticle && <ArticleModal article={selectedArticle} onClose={() => setSelectedArticle(null)} />}

            {/* Stadium pitch background */}
            <div className="fixed inset-0 pointer-events-none z-0">
                {/* Grass pitch grid */}
                <div className="absolute inset-0 pitch-grid opacity-40"
                     style={{transform: 'perspective(900px) rotateX(55deg) scale(2.4)', transformOrigin: 'bottom center'}} />
                {/* Pitch stripes */}
                <div className="absolute inset-0 pitch-stripe opacity-30" />
                {/* Center circle */}
                <div className="absolute top-[58%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-52 h-52 rounded-full border opacity-0 animate-[circle-glow_4s_ease-in-out_infinite]"
                     style={{borderColor: 'rgba(245,158,11,0.12)'}} />
                {/* Halfway line */}
                <div className="absolute top-[58%] left-0 right-0 h-px opacity-20"
                     style={{background: 'linear-gradient(90deg, transparent, rgba(245,158,11,0.3), transparent)'}} />
                {/* Ambient glows */}
                <div className="absolute top-[-15%] right-[-10%] w-[45%] h-[45%] bg-emerald-700/8 blur-[140px] rounded-full mix-blend-screen" />
                <div className="absolute bottom-[-20%] left-[-5%] w-[40%] h-[40%] bg-amber-600/5 blur-[120px] rounded-full mix-blend-screen" />
                {/* Stadium floodlights */}
                <div className="absolute top-0 left-1/4 w-1 h-24 bg-gradient-to-b from-amber-400/5 to-transparent blur-sm" />
                <div className="absolute top-0 right-1/4 w-1 h-24 bg-gradient-to-b from-amber-400/5 to-transparent blur-sm" />
            </div>

            <SearchHeader
                query={query} setQuery={setQuery} loading={loading}
                sentiment={sentiment} setSentiment={setSentiment}
                abMode={abMode} setAbMode={setAbMode}
                onSearch={handleSearch} onGoHome={goHome}
                queryTime={queryTime}
            />

            {searchError && (
                <div className="mx-8 mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 text-sm font-bold text-center backdrop-blur-md">
                    {searchError}
                </div>
            )}

            {abMode ? (
                <ABTestPanel results={results} baselineResults={baselineResults} tfidfResults={tfidfResults}
                              irMetrics={irMetrics} onSelectArticle={setSelectedArticle} />
            ) : (
                <main className={`mx-auto px-8 py-8 flex gap-8 relative z-10 transition-all duration-700 ${
                    isFullView ? 'w-full max-w-5xl' : 'max-w-7xl'
                }`}>
                    <div className={`transition-all duration-700 ${isFullView ? 'w-full' : 'flex-1 min-w-0'}`}>
                        {/* Entity link banner */}
                        {!isFullView && mappedQuery && !holoData && (
                            <div className="mb-6 flex items-center p-4 rounded-2xl border text-sm font-medium backdrop-blur-md"
                                 style={{background: 'rgba(16,185,129,0.06)', color: '#10b981', borderColor: 'rgba(16,185,129,0.15)'}}>
                                <Zap className="w-4 h-4 mr-2" />
                                实体链路：已将查询词 <b>"{query}"</b> 锚定为标准实体图谱 <b>"{mappedQuery}"</b>
                            </div>
                        )}

                        {/* Holo slice */}
                        <HoloSlice data={holoData} />

                        {/* Results */}
                        {results.length > 0 ? (
                            <div className="space-y-6">
                                {/* AI summary */}
                                {!isFullView && aiSummaryLoading && (
                                    <section className="p-6 rounded-3xl border backdrop-blur-sm animate-pulse"
                                             style={{background: 'rgba(15,30,20,0.4)', borderColor: 'rgba(16,185,129,0.1)'}}>
                                        <div className="h-4 rounded w-1/4 mb-4" style={{background: 'rgba(16,185,129,0.15)'}} />
                                        <div className="h-3 rounded w-full mb-2" style={{background: 'rgba(16,185,129,0.08)'}} />
                                        <div className="h-3 rounded w-5/6" style={{background: 'rgba(16,185,129,0.08)'}} />
                                    </section>
                                )}
                                {!isFullView && aiSummary && (
                                    <section className="p-6 rounded-3xl border backdrop-blur-md shadow-lg"
                                             style={{
                                                 background: 'linear-gradient(135deg, rgba(15,30,20,0.8), rgba(10,20,14,0.8))',
                                                 borderColor: 'rgba(245,158,11,0.15)',
                                             }}>
                                        <h3 className="flex items-center text-sm font-black mb-3 tracking-widest uppercase" style={{color: '#f59e0b'}}>
                                            <TrendingUp className="w-4 h-4 mr-2"/> AI 战况综述
                                        </h3>
                                        <p className="leading-relaxed text-sm" style={{color: '#cbd5e1'}}>{aiSummary}</p>
                                    </section>
                                )}

                                {/* Full view banner */}
                                {isFullView && (
                                    <div className="flex items-center mb-6 pb-4" style={{borderBottom: '1px solid rgba(16,185,129,0.1)'}}>
                                        <Radio className="w-5 h-5 mr-3 animate-pulse" style={{color: '#f59e0b'}} />
                                        <h3 className="text-xl font-black text-white tracking-widest uppercase">
                                            全息战况总览
                                            <span className="text-[10px] px-2 py-1 rounded ml-3 border font-mono"
                                                  style={{color: '#10b981', background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.15)'}}>GLOBAL UPLINK</span>
                                        </h3>
                                    </div>
                                )}

                                <div className={isFullView ? "grid grid-cols-1 md:grid-cols-2 gap-6" : "space-y-4"}>
                                    {results.map((item, idx) => (
                                        <div key={item.news_id} className="animate-card-rise" style={{animationDelay: `${idx * 0.06}s`}}>
                                            <NewsCard item={item} onClick={setSelectedArticle} />
                                        </div>
                                    ))}
                                </div>
                                {/* Load more */}
                                {results.length > 0 && results.length < totalResults && (
                                    <div className="flex justify-center mt-8">
                                        <button
                                            onClick={() => executeSearch(query, sentiment, true)}
                                            className="px-8 py-3 rounded-2xl font-bold text-sm transition-all group"
                                            style={{
                                                background: 'rgba(15,30,20,0.8)',
                                                border: '1px solid rgba(16,185,129,0.12)',
                                                color: '#cbd5e1',
                                            }}
                                            onMouseEnter={e => {
                                                e.target.style.borderColor = 'rgba(245,158,11,0.4)';
                                                e.target.style.color = '#f59e0b';
                                                e.target.style.background = 'rgba(20,35,25,0.9)';
                                            }}
                                            onMouseLeave={e => {
                                                e.target.style.borderColor = 'rgba(16,185,129,0.12)';
                                                e.target.style.color = '#cbd5e1';
                                                e.target.style.background = 'rgba(15,30,20,0.8)';
                                            }}>
                                            <span className="group-hover:animate-pulse">加载更多</span>
                                            <span className="block text-[10px] mt-0.5 font-normal" style={{color: '#64748b'}}>LOAD MORE RESULTS</span>
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            !isFullView && !loading && entityData ? (
                                <div className="backdrop-blur-md rounded-[2rem] p-8 border shadow-2xl relative overflow-hidden group"
                                     style={{background: 'rgba(15,30,20,0.45)', borderColor: 'rgba(16,185,129,0.12)'}}>
                                    <div className="absolute top-0 right-0 w-64 h-64 blur-[80px] rounded-full pointer-events-none"
                                         style={{background: 'rgba(245,158,11,0.06)'}} />
                                    <div className="flex items-center space-x-4 mb-8 relative z-10">
                                        <div className="w-12 h-12 rounded-2xl flex items-center justify-center border"
                                             style={{background: 'rgba(245,158,11,0.12)', color: '#f59e0b', borderColor: 'rgba(245,158,11,0.2)'}}>
                                            <User size={24} />
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-black tracking-widest uppercase" style={{color: '#f59e0b'}}>
                                                {entityType === 'player' ? 'AI 专属球探报告' : 'AI 俱乐部深度列传'}
                                            </h3>
                                        </div>
                                    </div>
                                    <h2 className="text-3xl md:text-4xl font-black text-white mb-8 tracking-wide relative z-10">
                                        {entityType === 'player' ? entityData.name : entityData.team_name}
                                        <span style={{color: '#10b981'}}> 档案解析</span>
                                    </h2>
                                    <div className="rounded-3xl p-8 border relative z-10 shadow-inner min-h-[200px]"
                                         style={{background: 'rgba(10,20,14,0.6)', borderColor: 'rgba(16,185,129,0.1)'}}>
                                        {aiBioLoading ? (
                                            <div className="animate-pulse space-y-4">
                                                <div className="h-4 rounded w-full" style={{background: 'rgba(16,185,129,0.12)'}} />
                                                <div className="h-4 rounded w-11/12" style={{background: 'rgba(16,185,129,0.12)'}} />
                                                <div className="h-4 rounded w-4/5" style={{background: 'rgba(16,185,129,0.12)'}} />
                                            </div>
                                        ) : (
                                            <p className="leading-loose text-lg font-medium whitespace-pre-line" style={{color: '#cbd5e1'}}>
                                                {aiBio || '正在呼叫 AI 引擎分析中...'}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                !loading && !holoData && (
                                    <div className={`flex flex-col items-center justify-center py-12 border-2 border-dashed rounded-3xl ${isFullView ? 'mt-12' : ''}`}
                                         style={{borderColor: 'rgba(16,185,129,0.1)'}}>
                                        <Search className="w-12 h-12 mb-4" style={{opacity: 0.15, color: '#64748b'}} />
                                        <p className="mb-4" style={{color: '#64748b'}}>{isFullView ? '全库暂无情报' : '未在系统全库中检索到相关情报'}</p>
                                        {spellSuggestions.length > 0 && (
                                            <div className="text-center">
                                                <p className="text-xs mb-3 font-mono uppercase tracking-wider" style={{color: '#475569'}}>可能是要找？</p>
                                                <div className="flex flex-wrap justify-center gap-2">
                                                    {spellSuggestions.map(s => (
                                                        <button key={s.term}
                                                                onClick={() => handleQuickSearch(s.term)}
                                                                className="px-4 py-1.5 rounded-full border text-sm font-bold transition-all cursor-pointer"
                                                                style={{
                                                                    background: 'rgba(16,185,129,0.08)',
                                                                    borderColor: 'rgba(16,185,129,0.2)',
                                                                    color: '#10b981',
                                                                }}
                                                                onMouseEnter={e => {
                                                                    e.target.style.background = 'rgba(245,158,11,0.12)';
                                                                    e.target.style.color = '#f59e0b';
                                                                    e.target.style.borderColor = 'rgba(245,158,11,0.4)';
                                                                }}
                                                                onMouseLeave={e => {
                                                                    e.target.style.background = 'rgba(16,185,129,0.08)';
                                                                    e.target.style.color = '#10b981';
                                                                    e.target.style.borderColor = 'rgba(16,185,129,0.2)';
                                                                }}>
                                                            {s.term}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )
                            )
                        )}
                    </div>

                    {/* Entity panel: always show, entity data takes priority over holo */}
                    {!isFullView && (
                        <EntityPanel
                            entityType={entityType} entityData={entityData}
                            onGraphClick={onGraphClick} loading={loading}
                            holoActive={!!holoData}
                        />
                    )}
                </main>
            )}
        </div>
    );
}
