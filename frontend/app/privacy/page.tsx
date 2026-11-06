export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-12 text-gray-900">
      <h1 className="text-2xl font-semibold">Privacy Policy</h1>
      <p className="mt-2 text-sm text-gray-500">Last updated: November 6, 2026</p>

      <h2 className="mt-8 text-lg font-semibold">What we collect</h2>
      <p className="mt-2 text-sm text-gray-700">
        When you sign in with Google, we receive your name, email address, and profile picture.
        We also store the tasks you create or are assigned, including titles, descriptions,
        priorities, due dates, and status.
      </p>

      <h2 className="mt-8 text-lg font-semibold">How we use it</h2>
      <p className="mt-2 text-sm text-gray-700">
        Your information is used only to sign you in, show you your tasks, let other users assign
        tasks to you, and send you email notifications when a task is created or completed.
        We do not sell or share your data with third parties.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Email</h2>
      <p className="mt-2 text-sm text-gray-700">
        Notifications are sent from a single application mailbox using the Gmail API. The app does
        not read your inbox and does not request access to your Gmail account.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Storage and security</h2>
      <p className="mt-2 text-sm text-gray-700">
        Data is stored in a managed PostgreSQL database. Your session is kept in a secure,
        httpOnly cookie.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Contact</h2>
      <p className="mt-2 text-sm text-gray-700">
        Questions or deletion requests: yashu.jaat880@gmail.com
      </p>
    </main>
  );
}