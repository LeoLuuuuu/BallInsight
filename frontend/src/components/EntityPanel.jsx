import ReactECharts from 'echarts-for-react';
import {
    User, Shield, MapPin, Trophy, Network, AlertCircle,
} from 'lucide-react';

function getRadarOption(player) {
    return {
        radar: {
            indicator: [
                { name: '速度', max: 100 }, { name: '射门', max: 100 },
                { name: '传球', max: 100 }, { name: '盘带', max: 100 },
                { name: '防守', max: 100 }, { name: '身体', max: 100 },
            ],
            shape: 'polygon',
            splitNumber: 4,
            axisName: { color: '#94a3b8', fontWeight: 600, fontSize: 10 },
            splitArea: { areaStyle: { color: ['rgba(10,25,15,0.8)', 'rgba(15,30,20,0.8)'] } },
            axisLine: { lineStyle: { color: '#1e3a28' } },
            splitLine: { lineStyle: { color: '#1e3a28' } },
        },
        series: [{
            type: 'radar',
            data: [{
                value: [player.pac, player.sho, player.pas, player.dri, player.def_attr, player.phy],
                name: player.name,
                areaStyle: { color: 'rgba(245, 158, 11, 0.3)' },
                lineStyle: { color: '#f59e0b', width: 2, shadowColor: '#f59e0b', shadowBlur: 10 },
                itemStyle: { color: '#f59e0b' },
            }],
        }],
    };
}

function getGraphOption(graphData) {
    return {
        tooltip: { trigger: 'item' },
        series: [{
            type: 'graph', layout: 'force',
            data: graphData.nodes, links: graphData.links,
            categories: [
                { name: 'Center', itemStyle: { color: '#f59e0b', shadowBlur: 20, shadowColor: '#f59e0b' } },
                { name: 'Team', itemStyle: { color: '#10b981', shadowBlur: 15, shadowColor: '#10b981' } },
                { name: 'Nation/League', itemStyle: { color: '#3b82f6', shadowBlur: 10, shadowColor: '#3b82f6' } },
                { name: 'Related', itemStyle: { color: '#64748b' } },
            ],
            roam: true,
            label: { show: true, position: 'right', formatter: '{b}', color: '#e2e8f0', fontSize: 11, fontWeight: 'bold' },
            force: { repulsion: 200, edgeLength: 70 },
            lineStyle: { color: '#334155', width: 1.5, curveness: 0.2 },
        }],
    };
}

export default function EntityPanel({ entityType, entityData, onGraphClick, loading, holoActive }) {
    if (loading) {
        return (
            <aside className="w-[380px] flex-shrink-0 sticky top-28 h-fit space-y-6">
                <div className="backdrop-blur-md rounded-[2rem] border border-dashed p-12 text-center animate-pulse"
                     style={{background: 'rgba(15,30,20,0.3)', borderColor: 'rgba(16,185,129,0.1)'}}>
                    <AlertCircle size={40} className="mx-auto mb-4 opacity-50" style={{color: '#ef4444'}} />
                    <p className="text-sm font-bold" style={{color: '#cbd5e1'}}>正在查询实体档案...</p>
                </div>
            </aside>
        );
    }

    if (!entityData) {
        return (
            <aside className="w-[380px] flex-shrink-0 sticky top-28 h-fit space-y-6">
                {holoActive ? (
                    <div className="backdrop-blur-md rounded-[2rem] border p-10 text-center flex flex-col items-center justify-center min-h-[300px]"
                         style={{
                             background: 'rgba(0,0,0,0.85)',
                             borderColor: 'rgba(245,158,11,0.25)',
                             boxShadow: '0 0 30px rgba(245,158,11,0.08)',
                         }}>
                        <Network className="w-16 h-16 mb-6" style={{color: '#f59e0b', animation: 'spin 4s linear infinite'}} />
                        <h3 className="text-lg font-black tracking-widest uppercase mb-2" style={{color: '#f59e0b'}}>Matrix Uplink Active</h3>
                        <div className="w-full h-1 rounded-full overflow-hidden mb-4" style={{background: '#1e3a28'}}>
                            <div className="h-full animate-pulse w-full" style={{background: '#f59e0b'}} />
                        </div>
                        <p className="text-xs font-mono" style={{color: 'rgba(245,158,11,0.5)'}}>常规档案显示协议已被全息时空回溯系统覆盖...</p>
                    </div>
                ) : (
                    <div className="backdrop-blur-md rounded-[2rem] border border-dashed p-12 text-center"
                         style={{background: 'rgba(15,30,20,0.3)', borderColor: 'rgba(16,185,129,0.1)'}}>
                        <AlertCircle size={40} className="mx-auto mb-4 opacity-50" style={{color: '#ef4444'}} />
                        <p className="text-sm font-bold" style={{color: '#cbd5e1'}}>数据库无此档案</p>
                    </div>
                )}
            </aside>
        );
    }

    return (
        <aside className="w-[380px] flex-shrink-0 sticky top-28 h-fit space-y-6">
            {/* Player / Team card */}
            <div className="backdrop-blur-xl rounded-[2rem] border shadow-2xl overflow-hidden relative group"
                 style={{background: 'linear-gradient(180deg, rgba(20,35,25,0.95), rgba(10,20,14,0.95))', borderColor: 'rgba(245,158,11,0.12)'}}>
                {/* Card shine */}
                <div className="absolute top-0 left-[-100%] w-[50%] h-full bg-gradient-to-r from-transparent via-white/[0.02] to-transparent skew-x-[-30deg] group-hover:left-[200%] transition-all duration-1000 pointer-events-none z-50" />

                {entityType === 'player' ? (
                    <>
                        <div className="p-6 relative border-b" style={{background: 'linear-gradient(180deg, rgba(30,45,35,0.8), rgba(10,20,14,0.9))', borderColor: 'rgba(16,185,129,0.1)'}}>
                            {/* OVR badge */}
                            <div className="absolute top-4 left-4 text-center z-20">
                                <div className="text-3xl font-black leading-none animate-score-pulse" style={{color: '#f59e0b'}}>{entityData.ovr}</div>
                                <div className="text-[10px] font-bold tracking-widest" style={{color: '#94a3b8'}}>{entityData.position}</div>
                            </div>
                            <div className="flex flex-col items-center mt-2 relative z-10">
                                <img
                                    src={`https://cdn.sofifa.net/players/rv/24/${entityData.sofifa_id}.png`}
                                    alt="" className="w-32 h-32 object-cover"
                                    style={{filter: 'drop-shadow(0 10px 10px rgba(0,0,0,0.5))'}}
                                    onError={(e) => e.target.src = 'https://ui-avatars.com/api/?name=P&background=0a1a10&color=f59e0b'} />
                                <h2 className="text-2xl font-black text-white mt-2 tracking-wide uppercase">{entityData.name}</h2>
                                <div className="flex items-center space-x-2 mt-1 text-xs font-bold" style={{color: '#94a3b8'}}>
                                    <img src={`https://cdn.sofifa.net/flags/${entityData.nation.toLowerCase()}.png`}
                                         className="h-3" alt=""
                                         onError={(e) => e.target.style.display = 'none'} />
                                    <span>{entityData.nation}</span><span>|</span><span>{entityData.team_name}</span>
                                </div>
                            </div>
                        </div>
                        <div className="p-4" style={{background: 'rgba(10,20,14,0.5)'}}>
                            <div className="h-56 -mx-4">
                                <ReactECharts option={getRadarOption(entityData)} style={{ height: '100%' }} />
                            </div>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="p-8 text-center relative border-b"
                             style={{background: 'linear-gradient(180deg, rgba(20,30,40,0.5), rgba(10,20,14,0.9))', borderColor: 'rgba(16,185,129,0.1)'}}>
                            <Shield className="absolute top-[-20px] right-[-20px] w-48 h-48 rotate-12" style={{color: 'rgba(16,185,129,0.04)'}} />
                            <div className="w-24 h-24 mx-auto rounded-full border-4 flex items-center justify-center mb-4 relative z-10"
                                 style={{background: '#0a1a10', borderColor: 'rgba(16,185,129,0.3)', boxShadow: '0 0 20px rgba(16,185,129,0.15)'}}>
                                <img src={`https://ui-avatars.com/api/?name=${entityData.team_name}&background=0a1a10&color=10b981&font-size=0.33`}
                                     className="rounded-full" alt="" />
                            </div>
                            <h2 className="text-2xl font-black text-white uppercase tracking-wider relative z-10">{entityData.team_name}</h2>
                            <p className="font-bold text-sm tracking-widest mt-1 uppercase relative z-10" style={{color: '#f59e0b'}}>{entityData.league}</p>
                        </div>
                        <div className="p-6 grid grid-cols-1 gap-4" style={{background: 'rgba(10,20,14,0.5)'}}>
                            <div className="flex items-center p-3 rounded-xl border"
                                 style={{background: 'rgba(15,30,20,0.4)', borderColor: 'rgba(16,185,129,0.1)'}}>
                                <MapPin className="w-5 h-5 mr-3" style={{color: '#94a3b8'}} />
                                <div>
                                    <p className="text-[10px] uppercase font-bold" style={{color: '#64748b'}}>主场 Stadium</p>
                                    <p className="text-sm font-bold" style={{color: '#e2e8f0'}}>{entityData.stadium || '未知主场'}</p>
                                </div>
                            </div>
                            <div className="flex items-center p-3 rounded-xl border"
                                 style={{background: 'rgba(15,30,20,0.4)', borderColor: 'rgba(16,185,129,0.1)'}}>
                                <Trophy className="w-5 h-5 mr-3" style={{color: '#f59e0b'}} />
                                <div>
                                    <p className="text-[10px] uppercase font-bold" style={{color: '#64748b'}}>联赛级别 League</p>
                                    <p className="text-sm font-bold" style={{color: '#e2e8f0'}}>{entityData.league}</p>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Knowledge graph */}
            {entityData.graph_data && (
                <div className="rounded-[2rem] border shadow-xl overflow-hidden"
                     style={{background: 'rgba(10,20,14,0.9)', borderColor: 'rgba(16,185,129,0.12)'}}>
                    <div className="px-5 py-4 border-b flex items-center justify-between"
                         style={{background: 'rgba(15,30,20,0.5)', borderColor: 'rgba(16,185,129,0.08)'}}>
                        <h4 className="text-xs font-black uppercase tracking-widest flex items-center" style={{color: '#f59e0b'}}>
                            <Network className="w-4 h-4 mr-2"/> 实体关联图谱
                        </h4>
                    </div>
                    <div className="h-64 relative" style={{background: 'linear-gradient(135deg, #0a1a10, #0d1f14)'}}>
                        <ReactECharts option={getGraphOption(entityData.graph_data)}
                                       onEvents={{ 'click': onGraphClick }}
                                       style={{ height: '100%', width: '100%' }} />
                    </div>
                </div>
            )}
        </aside>
    );
}
