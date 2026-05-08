import ReactECharts from 'echarts-for-react';
import { Search, Zap, FlaskConical, SplitSquareHorizontal, BarChart2, BookOpen } from 'lucide-react';

function getMetricsChartOption(metrics) {
    const tfidfP    = Number(metrics?.tfidf?.p_at_10 ?? 0);
    const tfidfNdcg = Number(metrics?.tfidf?.ndcg_at_10 ?? 0);
    const baselineP   = Number(metrics?.baseline?.p_at_10 ?? 0);
    const baselineNdcg = Number(metrics?.baseline?.ndcg_at_10 ?? 0);
    const oursP       = Number(metrics?.ours?.p_at_10 ?? 0);
    const oursNdcg    = Number(metrics?.ours?.ndcg_at_10 ?? 0);

    return {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function (params) {
                return params.map(item =>
                    `${item.seriesName}<br/>${item.name}: ${(item.value * 100).toFixed(1)}%`
                ).join('<br/><br/>');
            },
        },
        legend: { textStyle: { color: '#94a3b8' }, top: 0 },
        grid: { left: '3%', right: '4%', bottom: '5%', top: '15%', containLabel: true },
        xAxis: {
            type: 'value', max: 1,
            splitLine: { lineStyle: { color: '#1e3a28', type: 'dashed' } },
            axisLabel: { color: '#94a3b8', formatter: (v) => `${Math.round(v * 100)}%` },
        },
        yAxis: {
            type: 'category',
            data: ['P@10', 'NDCG@10'],
            axisLabel: { color: '#cbd5e1', fontWeight: 'bold' },
        },
        series: [
            {
                name: 'TF-IDF', type: 'bar',
                data: [tfidfP, tfidfNdcg],
                itemStyle: { color: '#f59e0b', borderRadius: [0, 4, 4, 0] },
                barWidth: 14,
                label: { show: true, position: 'right', color: '#f59e0b', fontSize: 10,
                         formatter: (item) => `${(item.value * 100).toFixed(1)}%` },
            },
            {
                name: 'BM25', type: 'bar',
                data: [baselineP, baselineNdcg],
                itemStyle: { color: '#475569', borderRadius: [0, 4, 4, 0] },
                barWidth: 14,
                label: { show: true, position: 'right', color: '#cbd5e1', fontSize: 10,
                         formatter: (item) => `${(item.value * 100).toFixed(1)}%` },
            },
            {
                name: 'Ours', type: 'bar',
                data: [oursP, oursNdcg],
                itemStyle: { color: '#10b981', borderRadius: [0, 4, 4, 0], shadowColor: '#10b981', shadowBlur: 10 },
                barWidth: 14,
                label: { show: true, position: 'right', color: '#10b981', fontSize: 10,
                         formatter: (item) => `${(item.value * 100).toFixed(1)}%` },
            },
        ],
    };
}

export default function ABTestPanel({ results, baselineResults, tfidfResults, irMetrics, onSelectArticle }) {
    return (
        <main className="flex-1 max-w-screen-2xl mx-auto w-full px-8 py-8 flex flex-col relative z-10">
            {/* Title */}
            <div className="flex items-center justify-center mb-8">
                <SplitSquareHorizontal className="w-8 h-8 mr-3" style={{color: '#f59e0b'}} />
                <h2 className="text-3xl font-black text-white tracking-widest uppercase">
                    三模型检索评估竞技场
                    <span className="text-sm align-top font-bold px-2 py-1 rounded ml-2"
                          style={{color: '#f59e0b', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)'}}>DEV MODE</span>
                </h2>
            </div>

            {/* Three-column comparison */}
            <div className="flex-1 flex gap-4 mb-8 min-h-[500px]">
                {/* TF-IDF column */}
                <div className="flex-1 rounded-3xl border p-5 flex flex-col"
                     style={{background: 'rgba(245,158,11,0.04)', borderColor: 'rgba(245,158,11,0.15)'}}>
                    <div className="flex items-center justify-between mb-4 pb-3" style={{borderBottom: '1px solid rgba(245,158,11,0.1)'}}>
                        <h3 className="font-bold uppercase tracking-widest text-sm flex items-center" style={{color: '#f59e0b'}}>
                            <BookOpen className="w-4 h-4 mr-2"/> TF-IDF 基线
                        </h3>
                        <span className="text-[10px] px-2 py-1 rounded border font-mono"
                              style={{color: '#f59e0b', background: 'rgba(245,158,11,0.08)', borderColor: 'rgba(245,158,11,0.2)'}}>余弦相似度</span>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar">
                        {tfidfResults.map((item, idx) => (
                            <div key={`tfidf-${idx}`} onClick={() => onSelectArticle(item)}
                                 className="p-3 rounded-xl border opacity-60 cursor-pointer hover:opacity-90 transition-opacity"
                                 style={{background: 'rgba(15,30,20,0.3)', borderColor: 'rgba(16,185,129,0.08)'}}>
                                <h4 className="text-xs font-bold mb-1 line-clamp-1" style={{color: '#cbd5e1'}}>{item.title.replace(/<[^>]+>/g, '')}</h4>
                                <p className="text-[10px] line-clamp-2" style={{color: '#64748b'}}>{item.snippet.replace(/<[^>]+>/g, '')}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* BM25 column */}
                <div className="flex-1 rounded-3xl border p-5 flex flex-col"
                     style={{background: 'rgba(15,30,20,0.25)', borderColor: 'rgba(16,185,129,0.1)'}}>
                    <div className="flex items-center justify-between mb-4 pb-3" style={{borderBottom: '1px solid rgba(16,185,129,0.08)'}}>
                        <h3 className="font-bold uppercase tracking-widest text-sm flex items-center" style={{color: '#94a3b8'}}>
                            <Search className="w-4 h-4 mr-2"/> BM25 基线
                        </h3>
                        <span className="text-[10px] px-2 py-1 rounded border font-mono"
                              style={{color: '#94a3b8', background: 'rgba(100,116,139,0.08)', borderColor: 'rgba(100,116,139,0.15)'}}>BM25(Raw)</span>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar">
                        {baselineResults.map((item, idx) => (
                            <div key={`base-${idx}`} onClick={() => onSelectArticle(item)}
                                 className="p-3 rounded-xl border opacity-60 cursor-pointer hover:opacity-90 transition-opacity"
                                 style={{background: 'rgba(15,30,20,0.3)', borderColor: 'rgba(16,185,129,0.08)'}}>
                                <h4 className="text-xs font-bold mb-1 line-clamp-1" style={{color: '#cbd5e1'}}>{item.title.replace(/<[^>]+>/g, '')}</h4>
                                <p className="text-[10px] line-clamp-2" style={{color: '#64748b'}}>{item.snippet.replace(/<[^>]+>/g, '')}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Ours column */}
                <div className="flex-1 rounded-3xl border p-5 flex flex-col relative"
                     style={{
                         background: 'linear-gradient(180deg, rgba(16,185,129,0.06), rgba(16,185,129,0.02))',
                         borderColor: 'rgba(16,185,129,0.2)',
                         boxShadow: 'inset 0 0 50px rgba(16,185,129,0.03)',
                     }}>
                    {/* Gold accent bar */}
                    <div className="absolute top-0 right-10 w-32 h-1"
                         style={{background: 'linear-gradient(90deg, #10b981, #f59e0b)', boxShadow: '0 0 10px rgba(245,158,11,0.3)'}} />
                    <div className="flex items-center justify-between mb-4 pb-3" style={{borderBottom: '1px solid rgba(16,185,129,0.15)'}}>
                        <h3 className="font-bold uppercase tracking-widest text-sm flex items-center" style={{color: '#10b981'}}>
                            <Zap className="w-4 h-4 mr-2"/> Ours 融合模型
                        </h3>
                        <span className="text-[10px] px-2 py-1 rounded border font-mono"
                              style={{color: '#6ee7b7', background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.3)'}}>BM25 × Time × Sent</span>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar">
                        {results.map((item, idx) => (
                            <div key={`adv-${idx}`} onClick={() => onSelectArticle(item)}
                                 className="p-3 rounded-xl border cursor-pointer transition-all gold-shimmer relative overflow-hidden"
                                 style={{
                                     background: 'rgba(15,30,20,0.7)',
                                     borderColor: 'rgba(16,185,129,0.2)',
                                     animation: `card-rise 0.35s ease-out ${idx * 0.06}s both`,
                                 }}
                                 onMouseEnter={e => {
                                     e.currentTarget.style.transform = 'translateY(-2px)';
                                     e.currentTarget.style.borderColor = 'rgba(245,158,11,0.35)';
                                     e.currentTarget.style.boxShadow = '0 4px 16px rgba(245,158,11,0.08)';
                                 }}
                                 onMouseLeave={e => {
                                     e.currentTarget.style.transform = 'none';
                                     e.currentTarget.style.borderColor = 'rgba(16,185,129,0.2)';
                                     e.currentTarget.style.boxShadow = 'none';
                                 }}>
                                <div className="flex justify-between items-start mb-1">
                                    <h4 className="text-xs font-bold flex-1 mr-3 line-clamp-1" style={{color: '#d1fae5'}}
                                        dangerouslySetInnerHTML={{ __html: item.title }} />
                                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border flex-shrink-0 animate-score-pulse"
                                          style={{
                                              color: '#f59e0b',
                                              background: 'rgba(245,158,11,0.12)',
                                              borderColor: 'rgba(245,158,11,0.25)',
                                          }}>
                                        {item.final_score?.toFixed(1)}
                                    </span>
                                </div>
                                <p className="text-[10px] line-clamp-2" style={{color: '#94a3b8'}}
                                   dangerouslySetInnerHTML={{ __html: item.snippet }} />
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Metrics chart - scoreboard style */}
            <div className="backdrop-blur-md rounded-3xl border p-6 shadow-2xl"
                 style={{background: 'rgba(15,30,20,0.8)', borderColor: 'rgba(16,185,129,0.12)'}}>
                <div className="flex items-center gap-8">
                    <div className="w-1/3 pr-8" style={{borderRight: '1px solid rgba(16,185,129,0.1)'}}>
                        <h3 className="text-xl font-black text-white flex items-center mb-2">
                            <BarChart2 className="w-5 h-5 mr-2" style={{color: '#f59e0b'}}/> IR 评价指标
                        </h3>
                        <p className="text-xs leading-relaxed" style={{color: '#94a3b8'}}>
                            三模型横向对比。{irMetrics?.grading === 'human' && (
                                <span className="block mt-2 font-bold" style={{color: '#f59e0b'}}>
                                    当前使用人工标注 ({irMetrics.human_labeled}/{irMetrics.total_candidates} 篇已标注)
                                </span>
                            )}
                        </p>
                        {irMetrics && (
                            <div className="mt-4 grid grid-cols-3 gap-2">
                                <div className="text-center p-2 rounded-lg border"
                                     style={{background: 'rgba(245,158,11,0.04)', borderColor: 'rgba(245,158,11,0.1)'}}>
                                    <div className="text-lg font-black" style={{color: '#f59e0b'}}>{(irMetrics.tfidf?.p_at_10 * 100).toFixed(0)}%</div>
                                    <div className="text-[9px]" style={{color: '#64748b'}}>TF-IDF P@10</div>
                                </div>
                                <div className="text-center p-2 rounded-lg border"
                                     style={{background: 'rgba(100,116,139,0.04)', borderColor: 'rgba(100,116,139,0.1)'}}>
                                    <div className="text-lg font-black" style={{color: '#cbd5e1'}}>{(irMetrics.baseline?.p_at_10 * 100).toFixed(0)}%</div>
                                    <div className="text-[9px]" style={{color: '#64748b'}}>BM25 P@10</div>
                                </div>
                                <div className="text-center p-2 rounded-lg border"
                                     style={{background: 'rgba(16,185,129,0.04)', borderColor: 'rgba(16,185,129,0.1)'}}>
                                    <div className="text-lg font-black" style={{color: '#10b981'}}>{(irMetrics.ours?.p_at_10 * 100).toFixed(0)}%</div>
                                    <div className="text-[9px]" style={{color: '#64748b'}}>Ours P@10</div>
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="flex-1 h-48">
                        <ReactECharts option={getMetricsChartOption(irMetrics)} notMerge={true}
                                       style={{ height: '100%', width: '100%' }} />
                    </div>
                </div>
            </div>
        </main>
    );
}
