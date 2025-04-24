-- Make sure the order column's unique key doesn't complain mid-update
update pokemon set "order" = -"order";
update pokemon_forms set "order" = -"order";

-- Set Pokémon order
with recursive families (pokemon_id, root_pokemon_id, path) as (
    select id, id, ARRAY[id] from pokemon where preevolution_id is null

    union all

    select
        pokemon.id,
        families.root_pokemon_id,
        families.path || ARRAY[pokemon.id]
    from
        families
        join pokemon on families.pokemon_id = pokemon.preevolution_id
),

family_order (root_pokemon_id, "order") as (
    select root_pokemon_id, min(pokemon_id)
    from families
    group by root_pokemon_id
),

pokemon_order (pokemon_id, "order") as (
    select
        families.pokemon_id,
        rank() over (order by family_order.order, families.path)
    from
        families
        join family_order on
            families.root_pokemon_id = family_order.root_pokemon_id
)

update pokemon set "order" = (
    select "order"
    from pokemon_order
    where pokemon_order.pokemon_id = pokemon.id
);

-- Set Pokémon form order
with form_order (pokemon_id, form_id, "order") as (
    select pokemon_id, form_id, rank() over (order by pokemon.order, form_id)
    from pokemon_forms join pokemon on pokemon_id = id
)

update pokemon_forms set "order" = (
    select "order"
    from form_order
    where (form_order.pokemon_id, form_order.form_id)
        = (pokemon_forms.pokemon_id, pokemon_forms.form_id)
);
