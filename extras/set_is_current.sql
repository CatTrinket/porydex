update pokemon_instances set is_current = (game_id, pokemon_id, form_id) in (
    select ranks.game_id, ranks.pokemon_id, ranks.form_id
    from (
        select
            pi.game_id, pi.pokemon_id, pi.form_id,
            rank() over (
                partition by pi.pokemon_id, pi.form_id
                order by
                    g.id in ('lets-go-pikachu', 'lets-go-eevee', 'legends-arceus'),
                    g.id desc
            ) as rank
        from
            pokemon_instances pi
            join games g on pi.game_id = g.id
    ) as ranks
    where ranks.rank = 1
);
