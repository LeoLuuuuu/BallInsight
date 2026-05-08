import { Terminal, Activity, Target } from 'lucide-react';

export default function HoloSlice({ data }) {
    if (!data) return null;

    return (
        <div className="mb-8 border rounded-3xl p-1 relative overflow-hidden"
             style={{
                 background: '#0a1a10',
                 borderColor: 'rgba(245,158,11,0.25)',
                 boxShadow: '0 0 40px rgba(245,158,11,0.12)',
             }}>
            <div className="absolute inset-0 mix-blend-screen pointer-events-none" style={{background: 'rgba(16,185,129,0.06)'}} />

            <div className="rounded-[1.4rem] p-6 relative overflow-hidden border"
                 style={{background: '#07100a', borderColor: 'rgba(16,185,129,0.1)'}}>
                {/* Scan lines */}
                <div className="absolute inset-0 pointer-events-none z-20 opacity-30"
                     style={{background: 'linear-gradient(transparent 50%, rgba(0,0,0,0.5) 50%)', backgroundSize: '100% 4px'}} />

                <div className="flex items-center justify-between mb-6 relative z-30 border-b pb-4"
                     style={{borderColor: 'rgba(245,158,11,0.15)'}}>
                    <div className="flex items-center space-x-3" style={{color: '#f59e0b'}}>
                        <div className="p-2 border rounded animate-pulse"
                             style={{background: 'rgba(245,158,11,0.1)', borderColor: 'rgba(245,158,11,0.3)'}}>
                            <Terminal size={20} />
                        </div>
                        <h3 className="text-xl font-black tracking-widest uppercase"
                            style={{
                                color: '#fbbf24',
                                textShadow: '0 0 8px rgba(245,158,11,0.5)',
                            }}>
                            {data.title}
                        </h3>
                    </div>
                    <div className="text-xs font-mono font-bold px-3 py-1 rounded flex items-center border"
                         style={{
                             color: '#ef4444',
                             background: 'rgba(239,68,68,0.08)',
                             borderColor: 'rgba(239,68,68,0.2)',
                         }}>
                        <div className="w-2 h-2 rounded-full mr-2 animate-ping" style={{background: '#ef4444'}} />
                        TOP SECRET // {data.date}
                    </div>
                </div>

                <div className="flex flex-col lg:flex-row gap-6 relative z-30">
                    <div className="w-full lg:w-3/5 aspect-video bg-black rounded-xl overflow-hidden border-2 relative flex-shrink-0 group"
                         style={{borderColor: 'rgba(16,185,129,0.2)', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.8)'}}>
                        <img src={data.media_url} alt=""
                             className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity" />
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
                            <Target className="w-24 h-24 animate-spin" style={{color: 'rgba(245,158,11,0.3)', animationDuration: '10s'}} strokeWidth={1} />
                        </div>
                        {/* Corner brackets */}
                        <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2" style={{borderColor: '#f59e0b'}} />
                        <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2" style={{borderColor: '#f59e0b'}} />
                        <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2" style={{borderColor: '#f59e0b'}} />
                        <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2" style={{borderColor: '#f59e0b'}} />
                    </div>

                    <div className="flex-1 flex flex-col justify-center space-y-4 p-4 rounded-xl border"
                         style={{background: 'rgba(0,0,0,0.4)', borderColor: 'rgba(16,185,129,0.08)'}}>
                        <h4 className="text-xs font-black uppercase tracking-widest flex items-center mb-2" style={{color: '#f59e0b'}}>
                            <Activity className="w-4 h-4 mr-2"/> 实时战术遥测分析
                        </h4>
                        <div className="space-y-3 font-mono">
                            {data.tactical_data.map((d, i) => (
                                <div key={i} className="flex items-start">
                                    <span className="mr-2" style={{color: '#10b981'}}>&gt;</span>
                                    <p className="text-sm font-bold tracking-tight" style={{color: '#6ee7b7'}}>{d}</p>
                                </div>
                            ))}
                        </div>
                        <div className="mt-4 pt-4 border-t" style={{borderColor: 'rgba(245,158,11,0.1)'}}>
                            <p className="text-[10px] font-mono animate-pulse" style={{color: 'rgba(245,158,11,0.5)'}}>
                                _UPLINK_SECURE_//_DATA_STREAM_ACTIVE
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
