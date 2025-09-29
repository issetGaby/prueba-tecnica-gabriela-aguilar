import { redirect } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

export default function HomePage() {
  if (isAuthenticated()) {
    redirect('/dashboard');
  } else {
    redirect('/login');
  }
}