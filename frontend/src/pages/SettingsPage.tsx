import { FormEvent, useState } from "react";
import { ThemePicker } from "@/components/ThemePicker";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { authApi, usersApi } from "@/lib/services";

export function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function saveProfile(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await usersApi.updateMe({ full_name: fullName });
      await refreshUser();
      setMessage("Profile updated.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function changePassword(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await authApi.changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setMessage("Password changed.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-enter mx-auto max-w-4xl space-y-6 text-slate-950">
      <div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-indigo-600">Personalize Suvyon</p><h2 className="mt-1 font-display text-3xl font-bold tracking-tight">Your account, your controls.</h2><p className="mt-2 text-sm text-slate-600">Manage appearance, profile details, and account security.</p></div>

      {message && (
        <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {message}
        </div>
      )}
      {error && (
        <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <div className="font-semibold">Appearance</div>
          <p className="mt-1 text-sm text-ink-500">
            Saved on this device only. Switching themes is a CSS change — nothing extra to host.
          </p>
        </div>
        <ThemePicker />
      </div>

      <form className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm space-y-4" onSubmit={saveProfile}>
        <div className="font-semibold">Profile</div>
        <div>
          <label className="label">Email</label>
          <input className="input" value={user?.email || ""} disabled />
        </div>
        <div>
          <label className="label">Full name</label>
          <input
            className="input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            minLength={2}
          />
        </div>
        <button className="btn-primary" disabled={saving}>
          Save profile
        </button>
      </form>

      <form className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm space-y-4" onSubmit={changePassword}>
        <div className="font-semibold">Change password</div>
        <div>
          <label className="label">Current password</label>
          <input
            className="input"
            type="password"
            required
            minLength={8}
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
        </div>
        <div>
          <label className="label">New password</label>
          <input
            className="input"
            type="password"
            required
            minLength={8}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </div>
        <button className="btn-outline" disabled={saving}>
          Update password
        </button>
      </form>
    </div>
  );
}
