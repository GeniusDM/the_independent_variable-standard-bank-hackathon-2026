import ClientTable from "@/components/ClientTable";
import { getClients } from "@/lib/api";

export default async function ClientsPage() {
  const clients = await getClients();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
          Clients
        </h1>
        <p className="text-sm text-slate-600">
          Full portfolio, sortable by opportunity and wallet gap
        </p>
      </div>
      <ClientTable clients={clients} />
    </div>
  );
}
