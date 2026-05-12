import { Link } from "@tanstack/react-router";
import { useAuth } from "@/hooks/use-auth";
import { useState } from "react";

export function AppNav() {
  const { user, logout } = useAuth();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true);
  };

  const confirmLogout = async () => {
    await logout();
    setShowLogoutConfirm(false);
    window.location.href = "/"; // Redirect to landing page
  };

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-[var(--line-strong)] bg-[color-mix(in_oklab,var(--ghost)_85%,transparent)] backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 h-16 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-3 font-display text-lg tracking-tight">
            <img src="/logo.png" alt="StandupBot" className="w-8 h-8 object-contain" />
            <span className="font-bold">StandupBot</span>
          </Link>

          {user && (
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-3">
                {user.avatar_url && (
                  <img
                    src={user.avatar_url}
                    alt={user.name}
                    className="w-8 h-8 rounded-full border border-[var(--line-strong)]"
                  />
                )}
                <div className="text-sm">
                  <div className="font-medium text-[var(--ink)]">{user.name}</div>
                  <div className="text-xs text-[var(--ink-soft)]">{user.email}</div>
                </div>
              </div>
              <button
                onClick={handleLogoutClick}
                className="text-sm font-medium text-[var(--ink-soft)] hover:text-[var(--ink)]"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={() => setShowLogoutConfirm(false)}
        >
          <div
            className="relative bg-[var(--surface)] border-2 border-[var(--line-strong)] w-full max-w-md mx-4 p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setShowLogoutConfirm(false)}
              className="absolute top-4 right-4 text-[var(--ink-soft)] hover:text-[var(--ink)]"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>

            {/* Modal content */}
            <div className="text-center mb-8">
              <img src="/logo.png" alt="StandupBot" className="w-16 h-16 mx-auto mb-4 object-contain" />
              <h2 className="font-display text-2xl font-bold text-[var(--ink)]">Log out?</h2>
              <p className="text-sm text-[var(--ink-soft)] mt-2">
                Are you sure you want to log out of StandupBot?
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={confirmLogout}
                className="btn-primary flex-1 justify-center"
              >
                Yes, log out
              </button>
              <button
                onClick={() => setShowLogoutConfirm(false)}
                className="btn-ghost flex-1 justify-center"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
