import type { RequestHandler } from './$types';

export const POST: RequestHandler = () => {
	// TODO ajouter un événement par L'ia
	// avoir un user IA dans la db pour le faire
	// auth l'ia via token / vérifier le token
	// avoir l'id du scénario
	// avoir les infos de l'événement
	// - Nouvel event ? (implique de l'ajouter dans la table event)
	// -- plus probable mais nécessite une formalisation côté bd/ia
	// - Event existant ? (implique des les créer au moment du scnéario)
	// Création de l'event
	// Création du noeud

	// TODO, voir comment afficher certains events en fonction du camp de la personne
	// - Gestion en bdd ?
	// - Panneau de choix de camp avant d'entrer dans la session pour la première fois ?

	return new Response(JSON.stringify({ message: 'success' }), { status: 200 });
};
