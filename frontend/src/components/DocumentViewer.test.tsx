import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { deleteDocument, getDocument } from "../api";
import { DocumentViewer } from "./DocumentViewer";

vi.mock("../api", () => ({
  getDocument: vi.fn(),
  deleteDocument: vi.fn(),
}));

const document = {
  filename: "ders.pdf",
  title: "Ders",
  file_type: "PDF",
  status: "ready" as const,
  chunk_count: 3,
};

beforeEach(() => {
  vi.mocked(getDocument).mockResolvedValue({
    ...document,
    character_count: 23,
    content: "PDF içinden çıkarılan gerçek metin.",
  });
  vi.mocked(deleteDocument).mockResolvedValue({
    filename: document.filename,
    document_count: 0,
    chunk_count: 0,
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("DocumentViewer", () => {
  it("belge içeriğini yükler ve silmeden önce onay ister", async () => {
    const onDeleted = vi.fn();
    render(<DocumentViewer document={document} onClose={() => undefined} onDeleted={onDeleted} />);

    expect(await screen.findByText("PDF içinden çıkarılan gerçek metin.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Belgeyi Sil" }));
    expect(screen.getByText(/kalıcı olarak silmek/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Evet, sil" }));

    await waitFor(() => expect(deleteDocument).toHaveBeenCalledWith("ders.pdf"));
    expect(onDeleted).toHaveBeenCalledWith("ders.pdf");
  });
});
