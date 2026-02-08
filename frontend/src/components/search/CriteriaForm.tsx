"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchModeSelector } from "./SearchModeSelector";
import { PresetSelector } from "./PresetSelector";
import type { SearchCriteria } from "@/types/api";
import {
  LOCATIONS,
  CERTIFICATIONS,
  MATERIALS,
  PRODUCTION_METHODS,
  BUDGET_TIERS,
} from "@/lib/constants";
import { Loader2, MapPin, Award, Layers, Scissors, DollarSign, Plus, X } from "lucide-react";

interface CriteriaFormProps {
  onSubmit: (criteria: SearchCriteria, mode: string, maxManufacturers: number) => void;
  isLoading?: boolean;
}

function CustomInput({
  placeholder,
  onAdd,
}: {
  placeholder: string;
  onAdd: (value: string) => void;
}) {
  const [value, setValue] = useState("");
  const handleAdd = () => {
    const trimmed = value.trim();
    if (trimmed) {
      onAdd(trimmed);
      setValue("");
    }
  };
  return (
    <div className="flex gap-2 mt-3">
      <Input
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleAdd();
          }
        }}
        className="flex-1"
      />
      <Button type="button" variant="outline" size="sm" onClick={handleAdd} disabled={!value.trim()}>
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  );
}

export function CriteriaForm({ onSubmit, isLoading }: CriteriaFormProps) {
  const [locations, setLocations] = useState<string[]>([]);
  const [moqMin, setMoqMin] = useState("");
  const [moqMax, setMoqMax] = useState("");
  const [certifications, setCertifications] = useState<string[]>([]);
  const [materials, setMaterials] = useState<string[]>([]);
  const [productionMethods, setProductionMethods] = useState<string[]>([]);
  const [budgetTier, setBudgetTier] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [customQueries, setCustomQueries] = useState("");
  const [searchMode, setSearchMode] = useState("auto");
  const [maxManufacturers, setMaxManufacturers] = useState(10);

  const toggleItem = (
    list: string[],
    setList: (v: string[]) => void,
    item: string
  ) => {
    setList(
      list.includes(item) ? list.filter((i) => i !== item) : [...list, item]
    );
  };

  const addCustomItem = (
    list: string[],
    setList: (v: string[]) => void,
    item: string
  ) => {
    if (!list.includes(item)) {
      setList([...list, item]);
    }
  };

  const presetLocations = LOCATIONS as readonly string[];
  const presetCertifications = CERTIFICATIONS as readonly string[];
  const presetMaterials = MATERIALS as readonly string[];
  const presetMethods = PRODUCTION_METHODS as readonly string[];

  const customLocations = locations.filter((l) => !presetLocations.includes(l));
  const customCertifications = certifications.filter((c) => !presetCertifications.includes(c));
  const customMaterials = materials.filter((m) => !presetMaterials.includes(m));
  const customMethods = productionMethods.filter((m) => !presetMethods.includes(m));

  const loadPreset = (criteria: SearchCriteria) => {
    setLocations(criteria.locations || []);
    setMoqMin(criteria.moq_min?.toString() || "");
    setMoqMax(criteria.moq_max?.toString() || "");
    setCertifications(criteria.certifications_of_interest || []);
    setMaterials(criteria.materials || []);
    setProductionMethods(criteria.production_methods || []);
    const tier = criteria.budget_tier;
    setBudgetTier(Array.isArray(tier) ? tier[0] || "" : tier || "");
    setAdditionalNotes(criteria.additional_notes || "");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const criteria: SearchCriteria = {
      locations: locations.length > 0 ? locations : undefined,
      moq_min: moqMin ? parseInt(moqMin) : undefined,
      moq_max: moqMax ? parseInt(moqMax) : undefined,
      certifications_of_interest:
        certifications.length > 0 ? certifications : undefined,
      materials: materials.length > 0 ? materials : undefined,
      production_methods:
        productionMethods.length > 0 ? productionMethods : undefined,
      budget_tier: budgetTier ? [budgetTier] : undefined,
      additional_notes: additionalNotes || undefined,
      custom_queries: customQueries
        ? customQueries.split("\n").filter(Boolean)
        : undefined,
    };
    onSubmit(criteria, searchMode, maxManufacturers);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between">
        <PresetSelector onSelect={loadPreset} />
      </div>

      {/* Search Mode */}
      <div className="space-y-2">
        <Label>Search Mode</Label>
        <SearchModeSelector value={searchMode} onChange={setSearchMode} />
      </div>

      {/* Locations */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary-500" />
            Locations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {LOCATIONS.map((loc) => (
              <button
                key={loc}
                type="button"
                onClick={() => toggleItem(locations, setLocations, loc)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  locations.includes(loc)
                    ? "bg-primary-100 text-primary-700 ring-1 ring-primary-300"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {loc}
              </button>
            ))}
            {customLocations.map((loc) => (
              <button
                key={loc}
                type="button"
                onClick={() => toggleItem(locations, setLocations, loc)}
                className="px-3 py-1.5 rounded-full text-sm font-medium transition-all bg-primary-100 text-primary-700 ring-1 ring-primary-300 flex items-center gap-1"
              >
                {loc}
                <X className="h-3 w-3" />
              </button>
            ))}
          </div>
          <CustomInput
            placeholder="Add custom location..."
            onAdd={(v) => addCustomItem(locations, setLocations, v)}
          />
        </CardContent>
      </Card>

      {/* MOQ Range */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary-500" />
            Minimum Order Quantity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="moqMin" className="text-xs">
                Min Units
              </Label>
              <Input
                id="moqMin"
                type="number"
                placeholder="e.g. 100"
                value={moqMin}
                onChange={(e) => setMoqMin(e.target.value)}
                min={0}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="moqMax" className="text-xs">
                Max Units
              </Label>
              <Input
                id="moqMax"
                type="number"
                placeholder="e.g. 5000"
                value={moqMax}
                onChange={(e) => setMoqMax(e.target.value)}
                min={0}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Certifications */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Award className="h-4 w-4 text-primary-500" />
            Certifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {CERTIFICATIONS.map((cert) => (
              <label
                key={cert}
                className="flex items-center gap-2 cursor-pointer"
              >
                <Checkbox
                  checked={certifications.includes(cert)}
                  onCheckedChange={() =>
                    toggleItem(certifications, setCertifications, cert)
                  }
                />
                <span className="text-sm text-gray-700">{cert}</span>
              </label>
            ))}
            {customCertifications.map((cert) => (
              <label
                key={cert}
                className="flex items-center gap-2 cursor-pointer"
              >
                <Checkbox
                  checked
                  onCheckedChange={() =>
                    toggleItem(certifications, setCertifications, cert)
                  }
                />
                <span className="text-sm text-primary-700 font-medium">{cert}</span>
              </label>
            ))}
          </div>
          <CustomInput
            placeholder="Add custom certification..."
            onAdd={(v) => addCustomItem(certifications, setCertifications, v)}
          />
        </CardContent>
      </Card>

      {/* Materials */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary-500" />
            Materials
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {MATERIALS.map((mat) => (
              <button
                key={mat}
                type="button"
                onClick={() => toggleItem(materials, setMaterials, mat)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  materials.includes(mat)
                    ? "bg-primary-100 text-primary-700 ring-1 ring-primary-300"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {mat}
              </button>
            ))}
            {customMaterials.map((mat) => (
              <button
                key={mat}
                type="button"
                onClick={() => toggleItem(materials, setMaterials, mat)}
                className="px-3 py-1.5 rounded-full text-sm font-medium transition-all bg-primary-100 text-primary-700 ring-1 ring-primary-300 flex items-center gap-1"
              >
                {mat}
                <X className="h-3 w-3" />
              </button>
            ))}
          </div>
          <CustomInput
            placeholder="Add custom material..."
            onAdd={(v) => addCustomItem(materials, setMaterials, v)}
          />
        </CardContent>
      </Card>

      {/* Production Methods */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Scissors className="h-4 w-4 text-primary-500" />
            Production Methods
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {PRODUCTION_METHODS.map((method) => (
              <button
                key={method}
                type="button"
                onClick={() =>
                  toggleItem(productionMethods, setProductionMethods, method)
                }
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  productionMethods.includes(method)
                    ? "bg-primary-100 text-primary-700 ring-1 ring-primary-300"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {method}
              </button>
            ))}
            {customMethods.map((method) => (
              <button
                key={method}
                type="button"
                onClick={() =>
                  toggleItem(productionMethods, setProductionMethods, method)
                }
                className="px-3 py-1.5 rounded-full text-sm font-medium transition-all bg-primary-100 text-primary-700 ring-1 ring-primary-300 flex items-center gap-1"
              >
                {method}
                <X className="h-3 w-3" />
              </button>
            ))}
          </div>
          <CustomInput
            placeholder="Add custom production method..."
            onAdd={(v) => addCustomItem(productionMethods, setProductionMethods, v)}
          />
        </CardContent>
      </Card>

      {/* Budget Tier */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-primary-500" />
            Budget Tier
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {BUDGET_TIERS.map((tier) => (
              <button
                key={tier}
                type="button"
                onClick={() =>
                  setBudgetTier(budgetTier === tier ? "" : tier)
                }
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium capitalize transition-all ${
                  budgetTier === tier
                    ? "bg-primary-600 text-white shadow-sm"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom Queries (shown for manual/hybrid) */}
      {(searchMode === "manual" || searchMode === "hybrid") && (
        <div className="space-y-2">
          <Label htmlFor="customQueries">Custom Search Queries</Label>
          <Textarea
            id="customQueries"
            placeholder="Enter one query per line..."
            value={customQueries}
            onChange={(e) => setCustomQueries(e.target.value)}
            rows={4}
          />
          <p className="text-xs text-gray-500">
            Enter one search query per line. These will be used to find manufacturers.
          </p>
        </div>
      )}

      {/* Additional Notes */}
      <div className="space-y-2">
        <Label htmlFor="notes">Additional Notes</Label>
        <Textarea
          id="notes"
          placeholder="Any specific requirements or preferences..."
          value={additionalNotes}
          onChange={(e) => setAdditionalNotes(e.target.value)}
          rows={3}
        />
      </div>

      {/* Max Manufacturers */}
      <div className="space-y-2">
        <Label htmlFor="maxMfg">Max Manufacturers to Find</Label>
        <Input
          id="maxMfg"
          type="number"
          value={maxManufacturers}
          onChange={(e) => setMaxManufacturers(parseInt(e.target.value) || 10)}
          min={1}
          max={50}
          className="w-32"
        />
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={isLoading}>
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isLoading ? "Starting Search..." : "Start Search"}
      </Button>
    </form>
  );
}
