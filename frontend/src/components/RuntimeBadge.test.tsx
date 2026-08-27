import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeBadge } from "./RuntimeBadge";

afterEach(cleanup);

describe("RuntimeBadge", () => {
  it("yalnızca backend verisine göre hazır durumunu gösterir", () => {
    render(
      <RuntimeBadge
        loading={false}
        health={{
          status: "ready",
          local: true,
          runtime: "ready",
          index_ready: true,
          chunk_count: 21,
          message: "Foundry Local modelleri hazır.",
        }}
      />,
    );

    expect(screen.getByLabelText("Foundry Local • Hazır")).toBeTruthy();
  });

  it("bağlantı yokken çevrimdışı durumunu gösterir", () => {
    render(<RuntimeBadge loading={false} health={null} />);
    expect(screen.getByLabelText("Yerel servis çevrimdışı")).toBeTruthy();
  });
});
