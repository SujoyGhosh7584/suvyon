import { Eye, EyeOff, LockKeyhole } from "lucide-react";
import { useState } from "react";

type Props = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: string;
  showStrength?: boolean;
};

export function PasswordField({ id, label, value, onChange, autoComplete, showStrength = false }: Props) {
  const [visible, setVisible] = useState(false);
  const score = [value.length >= 8, /[A-Z]/.test(value), /[a-z]/.test(value), /\d/.test(value), /[^A-Za-z0-9]/.test(value)].filter(Boolean).length;
  const strength = score <= 2 ? "Weak" : score <= 4 ? "Good" : "Strong";

  return (
    <div>
      <label className="label" htmlFor={id}>{label}</label>
      <div className="relative">
        <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" size={17} />
        <input
          id={id}
          className="input pl-10 pr-11"
          type={visible ? "text" : "password"}
          required
          minLength={8}
          maxLength={128}
          autoComplete={autoComplete}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-xl text-ink-400 hover:bg-ink-50 hover:text-ink-700"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? "Hide password" : "Show password"}
        >
          {visible ? <EyeOff size={17} /> : <Eye size={17} />}
        </button>
      </div>
      {showStrength && value && (
        <div className="mt-2 flex items-center gap-2">
          <div className="grid flex-1 grid-cols-5 gap-1">
            {[1, 2, 3, 4, 5].map((part) => (
              <span key={part} className={`h-1 rounded-full ${part <= score ? "bg-accent" : "bg-ink-100"}`} />
            ))}
          </div>
          <span className="text-xs font-medium text-ink-500">{strength}</span>
        </div>
      )}
    </div>
  );
}
