import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { SearchInput } from '../components/ui/SearchInput';
import { GlassCard } from '../components/ui/GlassCard';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { Modal } from '../components/ui/Modal';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import { Loading, Skeleton } from '../components/ui/Loading';
import { EmptyState } from '../components/ui/EmptyState';
import { DataTable } from '../components/ui/DataTable';
import { Pagination } from '../components/ui/Pagination';
import { StatCard } from '../components/ui/StatCard';
import { Tooltip } from '../components/ui/Tooltip';
import { PageHeader } from '../components/layout/PageHeader';
import { Inbox, CheckCircle2, ShieldCheck } from 'lucide-react';

export const Showcase: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  };

  const sampleData = [
    { id: 1, name: 'Google Cloud Platform', value: 1500, status: 'CONCLUIDA' },
    { id: 2, name: 'AWS Services', value: -450, status: 'PENDENTE_REVISAO' },
    { id: 3, name: 'Vercel Pro', value: 200, status: 'FALHA' },
  ];

  return (
    <div className="space-y-12 pb-20">
      <div className="flex items-center justify-between mb-8">
        <PageHeader 
          title="Design System Showcase" 
          description="Validação visual dos componentes UI criados com Glassmorphism e Tailwind." 
        />
        <Button variant="secondary" onClick={toggleDarkMode}>
          Toggle {darkMode ? 'Light' : 'Dark'} Mode
        </Button>
      </div>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">1. Buttons</h2>
        <div className="flex gap-4 flex-wrap">
          <Button variant="default">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Danger</Button>
          <Button variant="ghost">Ghost</Button>
          <Button isLoading>Loading</Button>
          <Button leftIcon={<CheckCircle2 className="w-4 h-4" />}>Com Ícone</Button>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">2. Glass Cards & Stats</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="Movimentações" value="4.502" trend="+12%" trendUp colorBorder="blue" />
          <StatCard title="Conciliados" value="4.200" trend="+15%" trendUp colorBorder="green" />
          <StatCard title="Pendentes" value="200" trend="-5%" trendUp={false} colorBorder="yellow" />
          <StatCard title="Divergências" value="102" colorBorder="red" />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">3. Inputs & Search</h2>
        <div className="max-w-md space-y-4">
          <Input placeholder="voce@exemplo.com" />
          <Input error />
          <SearchInput placeholder="Buscar transações..." />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">4. Badges & Status</h2>
        <div className="flex gap-4 flex-wrap">
          <Badge>Default</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="destructive">Error</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="glass">Glass</Badge>
          <div className="border-l pl-4 flex gap-4">
            <StatusBadge status="CONCLUIDA" />
            <StatusBadge status="PENDENTE_REVISAO" />
            <StatusBadge status="REJEITADO_PELO_MOTOR" />
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">5. Data Table & Pagination</h2>
        <GlassPanel className="p-4">
          <DataTable 
            data={sampleData}
            keyExtractor={(item) => item.id}
            columns={[
              { header: 'ID', accessor: 'id' },
              { header: 'Descrição', accessor: 'name' },
              { header: 'Valor', accessor: (item) => `R$ ${item.value.toFixed(2)}` },
              { header: 'Status', accessor: (item) => <StatusBadge status={item.status} /> }
            ]}
          />
          <div className="mt-4">
            <Pagination currentPage={currentPage} totalPages={5} onPageChange={setCurrentPage} />
          </div>
        </GlassPanel>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">6. Tabs (Radix)</h2>
        <Tabs defaultValue="t1" className="w-full max-w-md">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="t1">Dashboard</TabsTrigger>
            <TabsTrigger value="t2">Configurações</TabsTrigger>
          </TabsList>
          <TabsContent value="t1" className="p-4 glass rounded-lg mt-2">
            Conteúdo 1
          </TabsContent>
          <TabsContent value="t2" className="p-4 glass rounded-lg mt-2">
            Conteúdo 2
          </TabsContent>
        </Tabs>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">7. Modals & Dialogs</h2>
        <div className="flex gap-4">
          <Button onClick={() => setIsModalOpen(true)}>Abrir Modal Simples</Button>
          <Button variant="destructive" onClick={() => setIsConfirmOpen(true)}>Abrir Confirm Dialog</Button>
        </div>
        
        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Detalhes da Transação" footer={<Button onClick={() => setIsModalOpen(false)}>Fechar</Button>}>
          <p className="text-gray-600 dark:text-gray-300">Este é um exemplo de modal em glassmorphism.</p>
        </Modal>

        <ConfirmDialog 
          isOpen={isConfirmOpen} 
          onClose={() => setIsConfirmOpen(false)}
          title="Excluir Registro"
          message="Tem certeza que deseja excluir esta movimentação? Esta ação não pode ser desfeita."
          isDestructive
          onConfirm={() => console.log('Confirmado')}
        />
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">8. Loading & Empty State</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <GlassCard className="flex flex-col gap-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <div className="mt-4 border-t pt-4">
              <Loading text="Processando pipeline..." />
            </div>
          </GlassCard>
          
          <EmptyState 
            icon={Inbox}
            title="Nenhum arquivo importado"
            description="Faça o upload do extrato bancário para iniciar o processo de conciliação inteligente."
            actionLabel="Importar Extrato"
            onAction={() => {}}
          />
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">9. Tooltips</h2>
        <div className="flex gap-8 p-4">
          <Tooltip content="Informações verificadas pela auditoria">
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <ShieldCheck className="w-5 h-5 text-blue-500" /> Passe o mouse aqui
            </div>
          </Tooltip>
        </div>
      </section>
    </div>
  );
};
