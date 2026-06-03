export async function getHealth() {
  const res = await fetch('http://localhost:8000/health');
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}
