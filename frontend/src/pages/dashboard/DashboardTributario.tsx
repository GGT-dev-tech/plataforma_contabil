import React, { useEffect, useState } from 'react';
import { getDashboardData, DashboardData } from '../../services/api/analytics';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { TrendingUp, Landmark, Calculator, ReceiptText } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const COLORS = ['#6366f1', '#14b8a6', '#f43f5e', '#f59e0b'];

export const DashboardTributario: React.FC = () => {
  const { activeWorkspaceId } = useWorkspace();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fallback para mock se nao tiver workspace selecionado
        const id = activeWorkspaceId || "32ecbd0c-25d2-43bb-a30f-b1eaf602ed05";
        const result = await getDashboardData(id);
        setData(result);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeWorkspaceId]);

  if (loading || !data) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const retencoesCards = [
    { title: 'INSS Retido', value: data.retencoes.inss, icon: <Landmark className="w-6 h-6 text-emerald-400" />, color: 'from-emerald-500/20 to-transparent', border: 'border-emerald-500/20' },
    { title: 'ISS Retido', value: data.retencoes.iss, icon: <ReceiptText className="w-6 h-6 text-blue-400" />, color: 'from-blue-500/20 to-transparent', border: 'border-blue-500/20' },
    { title: 'IRRF Retido', value: data.retencoes.ir, icon: <Calculator className="w-6 h-6 text-rose-400" />, color: 'from-rose-500/20 to-transparent', border: 'border-rose-500/20' },
    { title: 'CSLL Retido', value: data.retencoes.csll, icon: <TrendingUp className="w-6 h-6 text-amber-400" />, color: 'from-amber-500/20 to-transparent', border: 'border-amber-500/20' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Dashboard Tributário
          </h1>
          <p className="text-gray-400 mt-1">
            Visão gerencial consolidada de retenções e regimes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {retencoesCards.map((card, idx) => (
          <div key={idx} className={`glass p-6 rounded-2xl border ${card.border} relative overflow-hidden group`}>
            <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${card.color} rounded-bl-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500`}></div>
            <div className="relative z-10">
              <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10 backdrop-blur-md">
                  {card.icon}
                </div>
              </div>
              <p className="text-gray-400 text-sm font-medium mb-1">{card.title}</p>
              <h3 className="text-2xl font-bold text-white">{formatCurrency(card.value)}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass p-6 rounded-2xl border border-white/5 h-[400px]">
          <h3 className="text-lg font-semibold text-white mb-6">Evolução de Entradas (Valor Bruto)</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.evolucao} margin={{ top: 5, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" tickFormatter={(value) => `R$ ${value / 1000}k`} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '0.5rem', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
                formatter={(value: any) => formatCurrency(Number(value))}
              />
              <Bar dataKey="valor" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass p-6 rounded-2xl border border-white/5 h-[400px]">
          <h3 className="text-lg font-semibold text-white mb-6">Obras por Regime Tributário</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data.obras_regime}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="quantidade"
                nameKey="regime"
              >
                {data.obras_regime.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', borderRadius: '0.5rem', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
