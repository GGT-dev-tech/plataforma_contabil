import React, { useEffect, useState } from 'react';
import { LineChart, LayoutDashboard, Wallet, TrendingUp, Building2, CheckCircle2 } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

interface DashboardDados {
  saldo_consolidado: number;
  total_receitas: number;
  total_despesas: number;
  vgv_aprovado: number;
  lucro_operacional: number;
}

export const DashboardHome: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [dados, setDados] = useState<DashboardDados | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('@App:token');
        const res = await fetch('/api/v1/analytics/dashboard', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setDados(await res.json());
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeWorkspace]);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 flex items-center gap-3">
            <LayoutDashboard className="w-8 h-8 text-primary-400" />
            Centro de Comando
          </h1>
          <p className="text-gray-400 mt-1">
            Visão consolidada da operação, funil de vendas e liquidez.
          </p>
        </div>
      </div>

      {!activeWorkspace ? (
        <div className="p-10 border border-white/10 rounded-2xl bg-white/5 text-center text-gray-400">
          Selecione uma Empresa no menu de configurações para ver os dados.
        </div>
      ) : loading || !dados ? (
        <div className="flex justify-center p-10">
          <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <>
          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl"></div>
              <div className="flex items-center gap-2 text-blue-400 mb-2">
                <Wallet className="w-5 h-5" />
                <span className="text-sm font-semibold uppercase tracking-wider">Saldo em Caixa</span>
              </div>
              <h2 className="text-3xl font-bold text-white">{formatCurrency(dados.saldo_consolidado)}</h2>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl"></div>
              <div className="flex items-center gap-2 text-emerald-400 mb-2">
                <CheckCircle2 className="w-5 h-5" />
                <span className="text-sm font-semibold uppercase tracking-wider">VGV Aprovado</span>
              </div>
              <h2 className="text-3xl font-bold text-white">{formatCurrency(dados.vgv_aprovado)}</h2>
              <p className="text-xs text-gray-500 mt-1">Negócios fechados no CRM</p>
            </div>

            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl"></div>
              <div className="flex items-center gap-2 text-purple-400 mb-2">
                <TrendingUp className="w-5 h-5" />
                <span className="text-sm font-semibold uppercase tracking-wider">Resultado Operacional</span>
              </div>
              <h2 className={`text-3xl font-bold ${dados.lucro_operacional >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {formatCurrency(dados.lucro_operacional)}
              </h2>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 w-24 h-24 bg-orange-500/10 rounded-full blur-2xl"></div>
              <div className="flex items-center gap-2 text-orange-400 mb-2">
                <Building2 className="w-5 h-5" />
                <span className="text-sm font-semibold uppercase tracking-wider">Receitas vs Despesas</span>
              </div>
              <div className="flex justify-between items-end mt-1">
                <div>
                  <p className="text-[10px] text-gray-500 uppercase">Receitas</p>
                  <p className="font-bold text-emerald-400">{formatCurrency(dados.total_receitas)}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-gray-500 uppercase">Despesas</p>
                  <p className="font-bold text-red-400">{formatCurrency(dados.total_despesas)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Gráfico Visual (Puro CSS) */}
          <div className="bg-white/5 border border-white/10 p-6 rounded-2xl mt-6">
            <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <LineChart className="w-5 h-5 text-gray-400" /> Comparativo Financeiro
            </h3>
            
            <div className="flex items-end gap-8 h-64 max-w-2xl mx-auto pb-6 border-b border-white/10 relative">
              {/* Grid Lines */}
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                <div className="w-full h-[1px] bg-white/5"></div>
                <div className="w-full h-[1px] bg-white/5"></div>
                <div className="w-full h-[1px] bg-white/5"></div>
                <div className="w-full h-[1px] bg-white/5"></div>
              </div>

              {/* Bar 1: Receitas */}
              <div className="flex-1 flex flex-col items-center justify-end h-full z-10 group">
                <div className="text-emerald-400 font-bold mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {formatCurrency(dados.total_receitas)}
                </div>
                <div 
                  className="w-24 bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t-xl shadow-[0_0_20px_rgba(52,211,153,0.3)] transition-all duration-1000"
                  style={{ height: dados.total_receitas > 0 ? '80%' : '10%' }}
                ></div>
                <p className="mt-4 text-sm font-semibold text-gray-400">Receitas Totais</p>
              </div>

              {/* Bar 2: Despesas */}
              <div className="flex-1 flex flex-col items-center justify-end h-full z-10 group">
                <div className="text-red-400 font-bold mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {formatCurrency(dados.total_despesas)}
                </div>
                <div 
                  className="w-24 bg-gradient-to-t from-red-600 to-red-400 rounded-t-xl shadow-[0_0_20px_rgba(248,113,113,0.3)] transition-all duration-1000"
                  style={{ height: dados.total_despesas > 0 ? (dados.total_despesas > dados.total_receitas ? '90%' : '50%') : '10%' }}
                ></div>
                <p className="mt-4 text-sm font-semibold text-gray-400">Despesas Totais</p>
              </div>
            </div>
            <p className="text-center text-xs text-gray-500 mt-4">Passe o mouse sobre as barras para ver os valores exatos.</p>
          </div>
        </>
      )}
    </div>
  );
};
