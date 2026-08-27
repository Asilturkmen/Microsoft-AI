import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ChatComposer } from "./ChatComposer";

afterEach(cleanup);

describe("ChatComposer", () => {
  it("Enter ile gönderir, Shift+Enter ile göndermez", () => {
    const onSubmit = vi.fn();
    render(
      <ChatComposer
        value="TCP nedir?"
        disabled={false}
        onChange={() => undefined}
        onSubmit={onSubmit}
        onUpload={() => undefined}
      />,
    );

    const textarea = screen.getByLabelText("Soru");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });
    expect(onSubmit).not.toHaveBeenCalled();
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("boş veya gönderim sırasında butonu devre dışı bırakır", () => {
    const { rerender } = render(
      <ChatComposer
        value="   "
        disabled={false}
        onChange={() => undefined}
        onSubmit={() => undefined}
        onUpload={() => undefined}
      />,
    );

    expect(
      (screen.getByRole("button", { name: "Soruyu gönder" }) as HTMLButtonElement).disabled,
    ).toBe(true);
    rerender(
      <ChatComposer
        value="Geçerli soru"
        disabled
        onChange={() => undefined}
        onSubmit={() => undefined}
        onUpload={() => undefined}
      />,
    );
    expect(
      (screen.getByRole("button", { name: "Soruyu gönder" }) as HTMLButtonElement).disabled,
    ).toBe(true);
  });
});
