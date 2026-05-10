import { useCallback, useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const emptyForm = {
  room: '',
  shelf_level: '',
  shelf_depth: '',
  color_name: '',
  color_code: '',
  finish_style: '',
  bucket_image_url: '',
  notes: '',
}

function App() {
  const [paints, setPaints] = useState([])
  const [roomSuggestions, setRoomSuggestions] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [search, setSearch] = useState('')
  const [editPaintId, setEditPaintId] = useState(null)
  const [error, setError] = useState('')

  const isEditing = editPaintId !== null

  const fetchPaints = useCallback(async (query = '') => {
    const url = new URL(`${API_BASE_URL}/paints`)
    if (query.trim()) {
      url.searchParams.set('query', query.trim())
    }

    const response = await fetch(url)
    return response.json()
  }, [])

  const fetchRooms = useCallback(async (suggest = '') => {
    const url = new URL(`${API_BASE_URL}/rooms`)
    if (suggest.trim()) {
      url.searchParams.set('suggest', suggest.trim())
    }

    const response = await fetch(url)
    return response.json()
  }, [])

  const loadPaints = useCallback(async (query = '') => {
    const data = await fetchPaints(query)
    setPaints(data)
  }, [fetchPaints])

  const loadRooms = useCallback(async (suggest = '') => {
    const data = await fetchRooms(suggest)
    setRoomSuggestions(data)
  }, [fetchRooms])

  useEffect(() => {
    const loadInitialData = async () => {
      await loadPaints()
      await loadRooms()
    }

    void loadInitialData()
  }, [loadPaints, loadRooms])

  useEffect(() => {
    const timeout = setTimeout(() => {
      void loadRooms(form.room)
    }, 200)
    return () => clearTimeout(timeout)
  }, [form.room, loadRooms])

  const roomOptions = useMemo(() => roomSuggestions.map((room) => room.name), [roomSuggestions])

  const handleFieldChange = (field, value) => {
    setForm((previous) => ({ ...previous, [field]: value }))
  }

  const resetForm = () => {
    setForm(emptyForm)
    setEditPaintId(null)
    setError('')
  }

  const handleSave = async () => {
    if (!form.room.trim() || !form.shelf_level.trim() || !form.shelf_depth.trim()) {
      setError('Room, shelf level, and shelf depth are required.')
      return
    }

    const method = isEditing ? 'PUT' : 'POST'
    const endpoint = isEditing ? `${API_BASE_URL}/paints/${editPaintId}` : `${API_BASE_URL}/paints`

    const payload = {
      ...form,
      room: form.room.trim(),
      shelf_level: form.shelf_level.trim(),
      shelf_depth: form.shelf_depth.trim(),
      color_name: form.color_name || null,
      color_code: form.color_code || null,
      finish_style: form.finish_style || null,
      bucket_image_url: form.bucket_image_url || null,
      notes: form.notes || null,
    }

    const response = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      setError('Unable to save paint entry. Please verify required fields.')
      return
    }

    resetForm()
    void loadPaints(search)
    void loadRooms()
  }

  const handleSearch = async () => {
    await loadPaints(search)
  }

  const beginEdit = (paint) => {
    setForm({
      room: paint.room,
      shelf_level: paint.shelf_level,
      shelf_depth: paint.shelf_depth,
      color_name: paint.color_name || '',
      color_code: paint.color_code || '',
      finish_style: paint.finish_style || '',
      bucket_image_url: paint.bucket_image_url || '',
      notes: paint.notes || '',
    })
    setEditPaintId(paint.id)
    setError('')
  }

  return (
    <main className="layout">
      <h1>Paint Tracker</h1>

      <section className="card">
        <h2>{isEditing ? 'Edit Paint' : 'Add Paint to Shelf'}</h2>
        <div className="grid">
          <label>
            Room *
            <input
              value={form.room}
              list="rooms"
              onChange={(event) => handleFieldChange('room', event.target.value)}
              placeholder="Living Room"
            />
          </label>
          <datalist id="rooms">
            {roomOptions.map((room) => (
              <option key={room} value={room} />
            ))}
          </datalist>

          <label>
            Shelf Level *
            <input
              value={form.shelf_level}
              onChange={(event) => handleFieldChange('shelf_level', event.target.value)}
              placeholder="A"
            />
          </label>

          <label>
            Shelf Depth *
            <input
              value={form.shelf_depth}
              onChange={(event) => handleFieldChange('shelf_depth', event.target.value)}
              placeholder="1"
            />
          </label>

          <label>
            Color Name
            <input
              value={form.color_name}
              onChange={(event) => handleFieldChange('color_name', event.target.value)}
              placeholder="Sea Mist"
            />
          </label>

          <label>
            Color Code
            <input
              value={form.color_code}
              onChange={(event) => handleFieldChange('color_code', event.target.value)}
              placeholder="SM-42"
            />
          </label>

          <label>
            Finish Style
            <input
              value={form.finish_style}
              onChange={(event) => handleFieldChange('finish_style', event.target.value)}
              placeholder="Satin"
            />
          </label>

          <label>
            Bucket Image URL
            <input
              value={form.bucket_image_url}
              onChange={(event) => handleFieldChange('bucket_image_url', event.target.value)}
              placeholder="https://..."
            />
          </label>

          <label className="full-width">
            Notes
            <textarea
              value={form.notes}
              onChange={(event) => handleFieldChange('notes', event.target.value)}
              placeholder="Where it was used"
            />
          </label>
        </div>

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button type="button" className="confirm" onClick={handleSave} title="Confirm">
            ✔
          </button>
          <button type="button" className="decline" onClick={resetForm} title="Decline">
            ✖
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Search Paints</h2>
        <div className="search-row">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search room, color, or coordinate"
          />
          <button type="button" onClick={handleSearch}>
            Search
          </button>
        </div>

        <ul className="paint-list">
          {paints.map((paint) => (
            <li key={paint.id}>
              <div>
                <strong>{paint.color_name || paint.color_code || 'Unnamed paint'}</strong>
                <p>
                  {paint.room} • {paint.shelf_level}-{paint.shelf_depth}
                </p>
                {paint.finish_style && <p>Finish: {paint.finish_style}</p>}
              </div>
              <button type="button" className="edit" onClick={() => beginEdit(paint)} title="Edit">
                ✏️
              </button>
            </li>
          ))}
          {paints.length === 0 && <li>No paints found.</li>}
        </ul>
      </section>
    </main>
  )
}

export default App
