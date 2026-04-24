"use client"

import { useState } from "react"

type DealerResult = { dealer: string; image: string }

const DEALERSHIP_DATA: Record<string, Record<string, string[]>> = {
  Volkswagen: {
    "North Region": ["VW-Dehradun", "VW-Gorakpur", "VW-Haladawani", "VW-Jodhpur"],
    "South Region": ["VW-Bangalore", "VW-Hubli"],
    "Other Dealers": ["VW-Apple", "VW-Autobhan", "VW-Frontier"],
  },
  Tata: {
    "Jasper Group": [
      "Jasper-tata-delhi",
      "Jasper-tata-guntur",
      "Jasper-tata-hyderabad",
      "Jasper-tata-vijayawada",
      "Jasper-tata-vizag",
    ],
    "Individual Dealers": [
      "Bellad-tata",
      "Jayaraj-tata",
      "Kaveri-tata",
      "Lakshmi-tata",
      "Shiva-tata",
      "true-sai",
    ],
  },
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000"

export default function Home() {
  const [selectedBrand, setSelectedBrand] = useState("Volkswagen")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedDealers, setSelectedDealers] = useState<string[]>([])
  const [expandedSections, setExpandedSections] = useState<string[]>(["north region"])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<DealerResult[]>([])
  const [error, setError] = useState("")


  const handleBrandChange = (brand: string) => {
    setSelectedBrand(brand)
    setSelectedDealers([])
    setResults([])
    const first = Object.keys(DEALERSHIP_DATA[brand])[0]
    setExpandedSections([first.toLowerCase()])
  }

  const handleDealerToggle = (dealer: string) => {
    setSelectedDealers((prev) =>
      prev.includes(dealer) ? prev.filter((d) => d !== dealer) : [...prev, dealer]
    )
  }

  const toggleSection = (section: string) => {
    const key = section.toLowerCase()
    setExpandedSections((prev) =>
      prev.includes(key) ? prev.filter((s) => s !== key) : [...prev, key]
    )
  }

  const handleSelectAll = () => {
    const all = Object.values(DEALERSHIP_DATA[selectedBrand]).flat()
    setSelectedDealers(all)
  }

  const handleClearAll = () => setSelectedDealers([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const generateCreative = async () => {
    if (!selectedFile) {
      alert("Please upload a background image first.")
      return
    }
    if (selectedDealers.length === 0) {
      alert("Please select at least one dealership.")
      return
    }

    const formData = new FormData()
    formData.append("image", selectedFile)
    formData.append("brand", selectedBrand)
    formData.append("dealers", JSON.stringify(selectedDealers))

    try {
      setLoading(true)
      setError("")
      setResults([])

      const res = await fetch(`${API_URL}/generate`, { method: "POST", body: formData })
      const data = await res.json()

      if (!res.ok || data.status !== "success") throw new Error(data.error || "Server error")

      const timestamped: DealerResult[] = data.results.map((r: DealerResult) => ({
        dealer: r.dealer,
        image: r.image + "?t=" + Date.now(),
      }))
      setResults(timestamped)
    } catch (err: any) {
      console.error(err)
      setError(err.message || "Generation failed. Is the Flask server running?")
    } finally {
      setLoading(false)
    }
  }

  const downloadZip = () => {
    window.open(`${API_URL}/download_zip`, "_blank")
  }

  const downloadSingle = (imageUrl: string, dealer: string) => {
    const a = document.createElement("a")
    a.href = imageUrl
    a.download = `creative_${dealer}.png`
    a.click()
  }

  return (
    <div className="h-screen overflow-hidden bg-slate-100 p-4">
      <div className="w-[95vw] h-[92vh] mx-auto bg-white text-slate-900 rounded-3xl shadow-xl overflow-hidden flex flex-col">


        <div className="bg-slate-950 text-white px-8 py-5 flex justify-between items-center shrink-0">
          <div className="text-2xl font-bold">CreativePilot AI</div>
          <div className="text-sm opacity-70">Ai powered creative generation for dealerships</div>
        </div>

        <div className="grid grid-cols-2 gap-8 p-8 flex-1 overflow-hidden">

          <div className="space-y-5 overflow-y-auto pr-2">


            <div>
              <h3 className="font-semibold mb-2">1. Select Brand</h3>
              <select
                className="w-full border rounded-xl p-3 bg-white"
                value={selectedBrand}
                onChange={(e) => handleBrandChange(e.target.value)}
              >
                {Object.keys(DEALERSHIP_DATA).map((b) => (
                  <option key={b}>{b}</option>
                ))}
              </select>
            </div>



            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">2. Select Dealership(s)</h3>
                <div className="flex gap-2 text-xs">
                  <button onClick={handleSelectAll} className="text-indigo-600 hover:underline">Select all</button>
                  <span className="text-gray-300">|</span>
                  <button onClick={handleClearAll} className="text-gray-500 hover:underline">Clear</button>
                </div>
              </div>

              <div className="border rounded-xl p-4 max-h-[300px] overflow-y-auto">
                {Object.entries(DEALERSHIP_DATA[selectedBrand]).map(([section, dealers]) => {
                  const key = section.toLowerCase()
                  const isExpanded = expandedSections.includes(key)
                  return (
                    <div key={section} className="mb-3">
                      <button
                        onClick={() => toggleSection(section)}
                        className="w-full flex justify-between items-center p-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition text-sm"
                      >
                        <span className="font-medium text-gray-700">{section}</span>
                        <span className="text-gray-400">{isExpanded ? "▼" : "▶"}</span>
                      </button>
                      {isExpanded && (
                        <div className="mt-2 ml-3 space-y-1">
                          {dealers.map((dealer) => (
                            <label key={dealer} className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                              <input
                                type="checkbox"
                                className="mr-2 accent-indigo-600"
                                checked={selectedDealers.includes(dealer)}
                                onChange={() => handleDealerToggle(dealer)}
                              />
                              <span className="text-sm">{dealer}</span>
                            </label>
                          ))}
                        </div>
                      )}
                    </div>
                  )

                })}
              </div>
            </div>


            <div>
              <h3 className="font-semibold mb-2">3. Upload Background Image</h3>
              <label
                htmlFor="bg-image-input"
                className="border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer hover:bg-gray-50 transition block"
              >
                <input
                  id="bg-image-input"
                  type="file"
                  accept="image/jpeg,image/png"
                  onChange={handleFileChange}
                  className="hidden"
                />
                {selectedFile ? (
                  <p className="text-green-600 text-sm font-medium">✓ {selectedFile.name}</p>
                ) : (
                  <>
                    <p className="text-gray-500 text-sm mb-1">Click to add background image</p>
                    <p className="text-gray-400 text-xs">JPG / PNG Original quality preserved</p>
                  </>
                )}
              </label>
            </div>


            <button
              onClick={generateCreative}
              disabled={loading}
              className="w-full bg-indigo-600 text-white rounded-xl py-4 font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? "Generating AI Creatives…" : "Generate AI Creatives"}
            </button>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 text-sm">
                {error}
              </div>
            )}
          </div>

          <div className="flex flex-col overflow-hidden">
            <div className="flex justify-between items-center mb-4 shrink-0">
              <h2 className="text-xl font-bold">Preview</h2>

              {results.length > 0 && (
                <button
                  onClick={downloadZip}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-2 rounded-lg transition font-semibold shadow-md"
                >
                  Download All
                </button>
              )}
            </div>


            {loading && (
              <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                Generating AI creatives, please wait…
              </div>
            )}

            {!loading && results.length > 0 && (
              <div className="flex-1 overflow-y-auto pr-2">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                  {results.map((r) => (
                    <div key={r.dealer} className="flex flex-col items-center">
                      <img
                        src={r.image}
                        alt={`creative-${r.dealer}`}
                        className="w-full aspect-square object-cover rounded-lg shadow-md mb-2"
                      />
                      <p className="text-xs font-medium text-center text-gray-700 truncate w-full">{r.dealer}</p>
                      <button
                        onClick={() => downloadSingle(r.image, r.dealer)}
                        className="mt-2 text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition font-medium"
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {!loading && results.length === 0 && (
              <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
                Select dealers and click Generate to preview creatives
              </div>
            )}
          </div>

        </div>

      </div>


    </div>
  )
}