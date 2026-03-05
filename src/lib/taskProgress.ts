/**
 * TODO: Remove this file on launch
 */

export type Task = {
	taskName: string;
	duration: number;
	subTasks?: Task[];
	completed: boolean;
	inCharge?: string;
	order?: number;
};

export const tasks: Task[] = [
	{
		taskName: 'Traduction',
		duration: 5,
		completed: false,
		order: 5
	},
	{
		taskName: 'Sessions',
		duration: 0,
		completed: true,
		order: 2,
		inCharge: 'Mathis',
		subTasks: [
			{
				taskName: 'Créer une session',
				duration: 5,
				completed: true
			},
			{
				taskName: 'Affichage sur la page d\'accueil',
				duration: 1,
				completed: true
			},
			{
				taskName: 'Page : Sessions',
				duration: 5,
				completed: true
			}
		]
	},
	{
		taskName: 'Admin',
		duration: 0,
		completed: true,
		inCharge: 'Mathis',
		order: 5,
		subTasks: [
			{
				taskName: 'Création de compte',
				duration: 5,
				completed: true
			},
			{
				taskName: 'Terminer une session',
				duration: 2,
				completed: true
			},
			{
				taskName: 'Ajouter un événement dans une session',
				duration: 8,
				completed: true
			},
			{
				taskName: 'Link les users aux sessions et aux scénarios',
				duration: 8,
				completed: true
			}
		]
	},
	{
		taskName: 'Graphe',
		duration: 0,
		completed: false,
		inCharge: 'Mathis',
		order: 3,
		subTasks: [
			{
				taskName: 'Voir les messages et les auteurs',
				duration: 4,
				completed: true
			},
			{
				taskName: 'Ajouter les sides aux messages',
				duration: 2,
				completed: true
			},
			{
				taskName: 'Couleur des noeuds',
				duration: 2,
				completed: false
			}
		]
	},
	{
		taskName: 'Page d\'accueil',
		duration: 0,
		completed: false,
		inCharge: 'Eva',
		order: 1,
		subTasks: [
			{
				taskName: 'Ajouter les dernières sessions',
				duration: 5,
				completed: true
			},
			{
				taskName: 'Design',
				duration: 15,
				completed: false
			}
		]
	}
];

export function sumTaskDuration(tasks: Task[]): number[] {
	const duration = tasks.reduce(
		(acc, task) => {
			if (task.completed) acc[0] = acc[0] + task.duration;
			acc[1] = acc[1] + task.duration;
			return acc;
		},
		[0, 0]
	);
	tasks.map((task) => {
		if (task.subTasks?.length) {
			const d = sumTaskDuration(task.subTasks);
			duration[0] += d[0];
			duration[1] += d[1];
		}
	});
	return duration;
}
