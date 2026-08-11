import React, { useEffect, useState } from 'react';
import { getDashboardData, DashboardData } from '../../services/api/analytics';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { TrendingUp, Landmark, Calculator, ReceiptText } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const COLORS = ['#2563eb', '#059669', '#e11d48', '#d97706'];

export const DashboardTributario: React.FC = () => {
  const { activeWorkspaceId } = useWorkspace();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
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
        <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const retencoesCards = [
    { title: 'INSS Retido', value: data.retencoes.inss, icon: <Landmark className="w-5 h-5 text-emerald-600" /> },
    { title: 'ISS Retido', value: data.retencoes.iss, icon: <ReceiptText className="w-5 h-5 text-blue-600" /> },
    { title: 'IRRF Retido', value: data.retencoes.ir, icon: <Calculator className="w-5 h-5 text-rose-600" /> },
    { title: 'CSLL Retido', value: data.retencoes.csll, icon: <TrendingUp className="w-5 h-5 text-amber-600" /> },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <ReceiptText className="w-8 h-8 text-primary-600" />
            Dashboard Tributário
          </h1>
          <p className="text-slate-500 mt-1">
            Visão gerencial consolidada de retenções e regimes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {retencoesCards.map((card, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                {card.icon}
              </div>
            </div>
            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">{card.title}</p>
            <h3 className="text-2xl font-bold text-slate-800">{formatCurrency(card.value)}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-[400px]">
          <h3 className="text-base font-bold text-slate-800 mb-6">Evolução de Entradas (Valor Bruto)</h3>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={data.evolucao} margin={{ top: 5, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" tickFormatter={(value) => `R$ ${value / 1000}k`} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '0.5rem', color: '#0f172a' }}
                itemStyle={{ color: '#0f172a' }}
                formatter={(value: any) => formatCurrency(Number(value))}
              />
              <Bar dataKey="valor" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-[400px]">
          <h3 className="text-base font-bold text-slate-800 mb-6">Obras por Regime Tributário</h3>
          <ResponsiveContainer width="100%" height="80%">
            <PieChart>
              <Pie
                data={data.obras_regime}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="quantidade"
                nameKey="regime"
              >
                {data.obras_regime.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '0.5rem', color: '#0f172a' }}
                itemStyle={{ color: '#0f172a' }}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
