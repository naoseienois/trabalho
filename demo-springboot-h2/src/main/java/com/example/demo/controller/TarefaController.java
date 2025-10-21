package com.example.demo.controller;

import com.example.demo.model.Tarefa;
import com.example.demo.repository.TarefaRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/tarefas")
public class TarefaController {

    private final TarefaRepository repository;

    public TarefaController(TarefaRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Tarefa> listarTodas() {
        return repository.findAll();
    }

    @GetMapping("/{id}")
    public Optional<Tarefa> listarPorId(@PathVariable Long id) {
        return repository.findById(id);
    }

    @PostMapping
    public List<Tarefa> criarTarefas(@RequestBody List<Tarefa> tarefas) {
        return repository.saveAll(tarefas);
    }

    @PutMapping("/{id}")
    public Tarefa atualizarTarefa(@PathVariable Long id, @RequestBody Tarefa novaTarefa) {
        return repository.findById(id).map(t -> {
            t.setNome(novaTarefa.getNome());
            t.setDataEntrega(novaTarefa.getDataEntrega());
            t.setResponsavel(novaTarefa.getResponsavel());
            return repository.save(t);
        }).orElseThrow(() -> new RuntimeException("Tarefa não encontrada"));
    }

    @DeleteMapping("/{id}")
    public void deletarTarefa(@PathVariable Long id) {
        repository.deleteById(id);
    }
}