import { ChangeEvent, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

type ProcessMethod =
    | "thresholding"
    | "skew"
    | "gaussian"
    | "median"
    | "bilateral"
    | "none";

interface UploadResponse {
    original: string;
    error?: string;
}

interface ProcessResponse {
    processed: string;
    error?: string;
}

interface ExtractResponse {
    text: string;
    error?: string;
}

interface ErrorResponse {
    error?: string;
    detail?: string;
}

const API_ORIGIN =
    import.meta.env.VITE_API_URL;

/**
 * Leave this empty if your router is registered like:
 *
 * server.include_router(router)
 *
 * If you later use:
 *
 * server.include_router(router, prefix="/ocr")
 *
 * set:
 *
 * VITE_OCR_API_PREFIX=/ocr
 */
const API_PREFIX = import.meta.env.VITE_OCR_API_PREFIX ?? "";

const MAX_FILE_SIZE = 16 * 1024 * 1024;

const allowedFileTypes = ["image/png", "image/jpeg"];

function apiUrl(path: string) {
    return `${API_ORIGIN}${API_PREFIX}${path}`;
}

function assetUrl(path: string) {
    if (path.startsWith("http://") || path.startsWith("https://")) {
        return path;
    }

    return new URL(path, `${API_ORIGIN}/`).toString();
}

async function getResponseData<T>(response: Response): Promise<T> {
    let data: T & ErrorResponse;

    try {
        data = await response.json();
    } catch {
        throw new Error(`Server returned HTTP ${response.status}`);
    }

    if (!response.ok) {
        throw new Error(
            data.error ||
            data.detail ||
            `Request failed with HTTP ${response.status}`,
        );
    }

    return data;
}

export function HomePage() {
    const [file, setFile] = useState<File | null>(null);

    const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(
        null,
    );

    const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(
        null,
    );

    const [processMethod, setProcessMethod] =
        useState<ProcessMethod>("thresholding");

    const [language, setLanguage] = useState("eng+vie");

    const [useOriginal, setUseOriginal] = useState(false);

    const [extractedText, setExtractedText] = useState("");

    const [error, setError] = useState<string | null>(null);

    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isExtracting, setIsExtracting] = useState(false);

    const currentImageUrl = useMemo(() => {
        if (useOriginal) {
            return originalImageUrl;
        }

        return processedImageUrl ?? originalImageUrl;
    }, [originalImageUrl, processedImageUrl, useOriginal]);

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];

        if (!selectedFile) {
            return;
        }

        setError(null);

        if (!allowedFileTypes.includes(selectedFile.type)) {
            setError("Only PNG, JPG and JPEG images are allowed.");
            event.target.value = "";
            return;
        }

        if (selectedFile.size > MAX_FILE_SIZE) {
            setError("The maximum allowed file size is 16 MB.");
            event.target.value = "";
            return;
        }

        setFile(selectedFile);

        // A new local file has not been uploaded to FastAPI yet.
        setOriginalImageUrl(null);
        setProcessedImageUrl(null);
        setExtractedText("");
        setUseOriginal(false);
    };

    const uploadImage = async () => {
        if (!file) {
            setError("Please select an image first.");
            return;
        }

        setIsUploading(true);
        setError(null);

        try {
            const formData = new FormData();

            /**
             * Matches:
             *
             * file: UploadFile = File(...)
             */
            formData.append("file", file);

            const response = await fetch(apiUrl("/upload"), {
                method: "POST",
                body: formData,
            });

            const data = await getResponseData<UploadResponse>(response);

            setOriginalImageUrl(assetUrl(data.original));

            setProcessedImageUrl(null);
            setExtractedText("");
            setUseOriginal(false);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Unable to upload the image.",
            );
        } finally {
            setIsUploading(false);
        }
    };

    const processImage = async () => {
        if (!originalImageUrl) {
            setError("Upload an image before processing it.");
            return;
        }

        setIsProcessing(true);
        setError(null);

        try {
            const response = await fetch(apiUrl("/process"), {
                method: "POST",
            });

            const data = await getResponseData<ProcessResponse>(response);

            setProcessedImageUrl(assetUrl(data.processed));

            // After processing, display/use the processed image.
            setUseOriginal(false);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Unable to process the image.",
            );
        } finally {
            setIsProcessing(false);
        }
    };

    const extractText = async () => {
        if (!originalImageUrl) {
            setError("Upload an image before extracting text.");
            return;
        }

        setIsExtracting(true);
        setError(null);

        try {
            const formData = new FormData();

            /**
             * Matches FastAPI:
             *
             * lang: str = Form(default="eng+vie")
             */
            formData.append("lang", language);

            const response = await fetch(apiUrl("/extract"), {
                method: "POST",
                body: formData,
            });

            const data = await getResponseData<ExtractResponse>(response);

            setExtractedText(data.text);
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Unable to extract text from the image.",
            );
        } finally {
            setIsExtracting(false);
        }
    };

    const clear = () => {
        setFile(null);

        setOriginalImageUrl(null);
        setProcessedImageUrl(null);

        setExtractedText("");
        setError(null);

        setUseOriginal(false);
    };

    return (
        <main className="mx-auto w-full max-w-7xl p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-semibold tracking-tight">
                    Image OCR
                </h1>

                <p className="mt-2 text-sm text-muted-foreground">
                    Upload an image, preprocess it and extract text using
                    Tesseract OCR.
                </p>
            </div>

            {error && (
                <div className="mb-6 rounded-md border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
                    {error}
                </div>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
                {/* LEFT SIDE */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Upload image</CardTitle>

                            <CardDescription>
                                Supported formats: PNG, JPG and JPEG. Maximum size:
                                16 MB.
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="ocr-image">
                                    Image
                                </Label>

                                <Input
                                    id="ocr-image"
                                    type="file"
                                    accept=".png,.jpg,.jpeg,image/png,image/jpeg"
                                    onChange={handleFileChange}
                                />
                            </div>

                            {file && (
                                <div className="rounded-md border bg-muted/40 p-3">
                                    <p className="text-sm font-medium">
                                        {file.name}
                                    </p>

                                    <p className="mt-1 text-xs text-muted-foreground">
                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-2">
                                <Button
                                    type="button"
                                    onClick={uploadImage}
                                    disabled={!file || isUploading}
                                >
                                    {isUploading ? "Uploading..." : "Upload"}
                                </Button>

                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={clear}
                                >
                                    Clear
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Image processing</CardTitle>

                            <CardDescription>
                                Apply preprocessing before running OCR.
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="space-y-5">
                            {/* <div className="space-y-2">
                                <Label>
                                    Processing method
                                </Label>

                                <Select
                                    value={processMethod}
                                    onValueChange={(value) =>
                                        setProcessMethod(value as ProcessMethod)
                                    }
                                >
                                    <SelectTrigger className="w-full">
                                        <SelectValue />
                                    </SelectTrigger>

                                    <SelectContent>
                                        <SelectItem value="thresholding">
                                            Otsu thresholding
                                        </SelectItem>

                                        <SelectItem value="skew">
                                            Deskew
                                        </SelectItem>

                                        <SelectItem value="gaussian">
                                            Gaussian blur
                                        </SelectItem>

                                        <SelectItem value="median">
                                            Median blur
                                        </SelectItem>

                                        <SelectItem value="bilateral">
                                            Bilateral filter
                                        </SelectItem>

                                        <SelectItem value="none">
                                            None
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div> */}

                            <Button
                                type="button"
                                variant="secondary"
                                className="w-full"
                                onClick={processImage}
                                disabled={!originalImageUrl || isProcessing}
                            >
                                {isProcessing
                                    ? "Processing..."
                                    : "Process image"}
                            </Button>

                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>OCR settings</CardTitle>

                            <CardDescription>
                                Select the Tesseract language model used for text
                                recognition.
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="space-y-5">
                            <div className="space-y-2">
                                <Label>
                                    Language
                                </Label>

                                <Select
                                    value={language}
                                    onValueChange={(value) => setLanguage(value!)}
                                >
                                    <SelectTrigger className="w-full">
                                        <SelectValue />
                                    </SelectTrigger>

                                    <SelectContent>
                                        <SelectItem value="eng+vie">
                                            English + Vietnamese
                                        </SelectItem>

                                        <SelectItem value="eng">
                                            English
                                        </SelectItem>

                                        <SelectItem value="vie">
                                            Vietnamese
                                        </SelectItem>

                                        <SelectItem value="fra">
                                            French
                                        </SelectItem>

                                        <SelectItem value="deu">
                                            German
                                        </SelectItem>

                                        <SelectItem value="spa">
                                            Spanish
                                        </SelectItem>

                                        <SelectItem value="jpn">
                                            Japanese
                                        </SelectItem>

                                        <SelectItem value="chi_sim">
                                            Chinese (Simplified)
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <Button
                                type="button"
                                className="w-full"
                                onClick={extractText}
                                disabled={!originalImageUrl || isExtracting}
                            >
                                {isExtracting
                                    ? "Extracting text..."
                                    : "Extract text"}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* RIGHT SIDE */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Image preview</CardTitle>

                            <CardDescription>
                                {useOriginal
                                    ? "Currently using the original image."
                                    : processedImageUrl
                                        ? "Currently using the processed image."
                                        : "Original uploaded image."}
                            </CardDescription>
                        </CardHeader>

                        <CardContent>
                            {currentImageUrl ? (
                                <div className="flex min-h-[400px] items-center justify-center overflow-hidden rounded-lg border bg-muted/30">
                                    <img
                                        src={currentImageUrl}
                                        alt="OCR preview"
                                        className="max-h-[600px] max-w-full object-contain"
                                    />
                                </div>
                            ) : (
                                <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                                    <p className="text-sm text-muted-foreground">
                                        Upload an image to preview it here.
                                    </p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Extracted text</CardTitle>

                            <CardDescription>
                                Text recognized by Tesseract OCR.
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            <Textarea
                                value={extractedText}
                                onChange={(event) =>
                                    setExtractedText(event.target.value)
                                }
                                placeholder="Extracted text will appear here..."
                                className="min-h-[300px] resize-y font-mono"
                            />

                            <Button
                                type="button"
                                variant="outline"
                                disabled={!extractedText}
                                onClick={() =>
                                    navigator.clipboard.writeText(
                                        extractedText,
                                    )
                                }
                            >
                                Copy text
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </main>
    );
}